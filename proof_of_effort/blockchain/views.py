from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .blockchain import Blockchain, Block
from .network import add_node, get_nodes, broadcast_block, get_broadcast_logs, auto_discover_peers, sync_chain
from .validator import EffortValidator, verify_proof
from .models import UserWallet, TokenLedger, PendingEffort
from .serializers import WalletSerializer, RegisterSerializer, UserInfoSerializer
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
import json
from django.core.files.storage import FileSystemStorage
from .chain import blockchain
validator = EffortValidator()


@api_view(['GET'])
def leaderboard_view(request):
    scores = (
        TokenLedger.objects
        .values('user__user__username')
        .annotate(total_score=Sum('amount'))
        .order_by('-total_score')
    )

    data = [
        {"username": entry["user__user__username"], "total_score": entry["total_score"]}
        for entry in scores
    ]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_efforts(request):
    efforts = []

    for block in blockchain.chain:
        # Skip genesis
        if block.index == 0:
            continue

        efforts.append({
            "index": block.index,
            "effort_data": block.effort_data,
            "timestamp": block.timestamp,
            "validated_by": block.validated_by
        })

    return Response({ "chain": efforts })  # ✅ Wrap it in a key like frontend expects

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    wallet = UserWallet.objects.filter(user=user).first()
    if not wallet:
        return Response({"error": "Wallet not found"}, status=404)

    # Token balance
    history = TokenLedger.objects.filter(user=wallet)
    total = history.aggregate(total=models.Sum("amount"))["total"] or 0

    # Efforts
    effort_history = [
        block.to_dict() for block in blockchain.chain
        if block.effort_data.get("user_id") == user.username
    ]

    return Response({
        "user": {
            "username": user.username,
            "role": wallet.role,
            "public_key": wallet.public_key
        },
        "token_balance": total,
        "efforts": effort_history,
        "effort_count": len(effort_history)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validator_dashboard(request):
    user = request.user
    wallet = UserWallet.objects.filter(user=user, role='validator').first()
    if not wallet:
        return Response({"error": "Not authorized"}, status=403)

    validated_blocks = [
        block.to_dict() for block in blockchain.chain
        if block.validated_by == user.username and block.index != 0  # exclude genesis
    ]
    return Response({
        "validated_efforts": validated_blocks,
        "total_validated": len(validated_blocks)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_token_history(request):
    wallet = UserWallet.objects.filter(user=request.user).first()
    if not wallet:
        return Response({"error": "Wallet not found"}, status=404)

    history = TokenLedger.objects.filter(user=wallet).order_by("-timestamp")
    total = history.aggregate(total=models.Sum("amount"))["total"] or 0

    data = [
        {
            "amount": t.amount,
            "source_block_index": t.source_block_index,
            "reason": t.reason,
            "timestamp": t.timestamp
        }
        for t in history
    ]

    return Response({
        "token_balance": total,
        "transactions": data
    })

@api_view(['POST'])
def register_wallet(request):
    serializer = WalletSerializer(data=request.data)
    if serializer.is_valid():
        existing = UserWallet.objects.filter(user=serializer.validated_data['user']).first()
        if existing:
            return Response({"error": "Wallet already registered"}, status=400)
        serializer.save()
        return Response({"message": "Wallet registered"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def connect_node(request):
    data = request.data
    nodes = data.get("nodes")

    if not nodes or not isinstance(nodes, list):
        return Response({"error": "Invalid nodes"}, status=400)

    for node in nodes:
        add_node(node)

    # Discover additional peers & sync chain
    auto_discover_peers()
    sync_chain()

    return Response({
        "message": "Nodes added & chain synced",
        "total": len(get_nodes()),
        "nodes": get_nodes()
    })

@api_view(['POST'])
def receive_block(request):
    block_data = request.data.get("block")
    print("Incoming block data:", block_data)

    if not block_data:
        return Response({"error": "No block provided"}, status=400)

    try:
        block = Block.from_dict(block_data)
    except Exception as e:
        print("Block.from_dict failed:", str(e))
        return Response({"error": f"Failed to rebuild block: {str(e)}"}, status=400)

    last_block = blockchain.get_last_block()
    print("Last block:", last_block.index, last_block.hash)
    print("New block:", block.index, block.previous_hash)

    if blockchain.is_valid_block(block, last_block):
        blockchain.chain.append(block)
        return Response({"message": "Block accepted"}, status=201)
    else:
        print("Block is invalid based on chain rules.")
        return Response({"error": "Invalid block"}, status=400)
    
@api_view(['GET'])
def sync_chain_view(request):
    success = sync_chain()

    if success:
        return Response({"message": "Chain replaced with longest valid chain"})
    return Response({"message": "Current chain is already the longest valid"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def queue_effort(request):
    data = request.data
    effort_data = data.get('effort_data')
    user_signature = data.get('user_signature')
    user_public_key = data.get('user_public_key')
    validator_id = data.get('validator_id')  # ✅ Accept it

    if not effort_data or not user_public_key:
        return Response({"error": "Missing required fields"}, status=400)

    user_id = effort_data.get("user_id")
    user_wallet = UserWallet.objects.filter(user__username=user_id).first()
    # if not user_wallet or user_wallet.public_key != user_public_key:
    #     return Response({"error": "User wallet not valid"}, status=400)

    if user_wallet.public_key.lstrip('04') != user_public_key.lstrip('04'):
        return Response({"error": "User wallet not valid"}, status=400)

    if user_wallet.role == 'student':
        if not user_signature:
            return Response({"error": "Student effort must include a user_signature"}, status=400)
        
        result = verify_proof(effort_data, user_signature, user_public_key, debug=True)
        if isinstance(result, dict):
            return Response({"error": "User signature invalid", "debug": result}, status=400)

    # ✅ Save to queue, include validator_id if present
    PendingEffort.objects.create(
        effort_data=effort_data,
        user_signature=user_signature,
        user_public_key=user_public_key,
        submitted_by=user_id,
        assigned_validator=validator_id  # ✅ Save here
    )

    return Response({"message": "Effort queued for validation"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({"error": "No file provided"}, status=400)

    fs = FileSystemStorage()
    filename = fs.save(uploaded_file.name, uploaded_file)
    file_url = fs.url(filename)
    full_url = request.build_absolute_uri(file_url)

    return Response({"file_url": full_url})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_efforts(request):
    user = request.user
    wallet = UserWallet.objects.filter(user=user, role='validator').first()
    if not wallet:
        return Response({"error": "Not authorized"}, status=403)

    # Optionally: filter only efforts assigned to this validator
    efforts = PendingEffort.objects.filter(is_expired=False).order_by('-submitted_at')

    data = []
    for e in efforts:
        data.append({
            "id": e.id,
            "effort_data": e.effort_data,
            "submitted_by": e.submitted_by,
            "submitted_at": e.submitted_at,
            "assigned_validator": e.assigned_validator,
            "is_expired": e.is_expired
        })

    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_effort(request, effort_id):  # <- Accept effort_id from URL
    user = request.user
    validator_wallet = UserWallet.objects.filter(user=user, role='validator').first()
    if not validator_wallet:
        return Response({"error": "Not authorized"}, status=403)

    validator_signature = request.data.get('validator_signature')

    if not validator_signature:
        return Response({"error": "Missing validator_signature"}, status=400)

    try:
        effort = PendingEffort.objects.get(id=effort_id, is_expired=False)
    except PendingEffort.DoesNotExist:
        return Response({"error": "Effort not found or already processed"}, status=404)

    effort_data = effort.effort_data
    user_signature = effort.user_signature
    user_public_key = effort.user_public_key
    submitted_by = effort.submitted_by

    # Re-check user wallet
    user_wallet = UserWallet.objects.filter(user__username=submitted_by).first()
    stored_key = user_wallet.public_key.lstrip('04')
    submitted_key = user_public_key.lstrip('04')

    if stored_key != submitted_key:
        return Response({"error": "User wallet not valid"}, status=400)

    # if not user_wallet or user_wallet.public_key != user_public_key:
    #     return Response({"error": "User wallet not valid"}, status=400)

    # Re-verify user signature
    if not verify_proof(effort_data, user_signature, user_public_key):
        return Response({"error": "User signature invalid"}, status=400)

    # Verify validator signature
    if not verify_proof(effort_data, validator_signature, validator_wallet.public_key):
        return Response({"error": "Validator signature invalid"}, status=400)

    # Validate effort data
    validator = EffortValidator()
    if not validator.is_valid(effort_data, user.username):
        return Response({"error": "Effort data invalid"}, status=400)

    # Add to chain
    proof = {
        "user_signature": user_signature,
        "validator_signature": validator_signature
    }

    block = blockchain.add_block(
        effort_data=effort_data,
        validated_by=user.username,
        proof=proof,
        user_public_key=user_public_key
    )

    if block:
        # Mark effort as processed
        effort.is_expired = True
        effort.assigned_validator = user.username
        effort.save()

        broadcast_block(block)

        return Response({
            "message": "Effort approved and block added",
            "block": block.to_dict()
        })
    else:
        return Response({"error": "Failed to add block"}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_effort(request, effort_id):
    user = request.user
    validator_wallet = UserWallet.objects.filter(user=user, role='validator').first()
    if not validator_wallet:
        return Response({"error": "Not authorized"}, status=403)

    # effort_id = request.data.get('effort_id')
    reason = request.data.get('reason', 'Rejected by validator')

    if not effort_id:
        return Response({"error": "Missing effort ID"}, status=400)

    try:
        effort = PendingEffort.objects.get(id=effort_id, is_expired=False)
    except PendingEffort.DoesNotExist:
        return Response({"error": "Effort not found or already processed"}, status=404)

    effort.is_expired = True
    effort.assigned_validator = user.username
    effort.rejection_reason = reason
    effort.save()

    return Response({"message": "Effort rejected", "reason": reason})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_rejected_efforts(request):
    user = request.user
    wallet = UserWallet.objects.filter(user=user, role='validator').first()
    if not wallet:
        return Response({"error": "Not authorized"}, status=403)

    # Filter efforts rejected by this validator
    rejected = PendingEffort.objects.filter(
        assigned_validator=user.username,
        is_expired=True,
    ).exclude(rejection_reason__isnull=True).order_by("-submitted_at")

    data = [
        {
            "id": e.id,
            "task_id": e.effort_data.get("task_id"),
            "user_id": e.submitted_by,
            "submitted_at": e.submitted_at,
            "reason": e.rejection_reason,
            "file_url": e.effort_data.get("submission", {}).get("file_url"),  # 👈 this line
        }
        for e in rejected
    ]

    return Response(data)

@api_view(['GET'])
def get_chain(request):
    chain_data = [block.__dict__ for block in blockchain.chain]
    return Response({"length": len(chain_data), "chain": chain_data})

@api_view(['GET'])
def validate_chain(request):
    is_valid = blockchain.is_valid_chain()
    return Response({"valid": is_valid})

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered'})
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def user_info_view(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
    serializer = UserInfoSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_me_view(request):
    serializer = UserInfoSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
def list_peers(request):
    return Response({"peers": get_nodes()})

@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok"})

@api_view(['GET'])
def block_height(request):
    return Response({"height": len(blockchain.chain)})
