from .models import Group, Plan, Category
from accounts.models import User
from .serializers import GroupSerializer, PlanSerializer, CategorySerializer, InviteMemberSerializer, JoinMemberSerializer
from rest_framework.viewsets import ModelViewSet, ViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import jwt, string, random, requests, json
from travellion.settings import JWT_SECRET_KEY

from rest_framework.permissions import IsAuthenticated
from .permissions import IsGroupLeader, IsGroupMember
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView

from datetime import datetime, time, timedelta
from django.core.mail import send_mail
from rest_framework.decorators import action
import os


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def set_leader(self, request, pk=None):
        group = self.get_object()

        new_leader_id = request.data.get('new_leader_id', None)
        
        if new_leader_id:
            new_leader = User.objects.get(pk=new_leader_id)

            if request.user == group.leader:
                group.set_new_leader(new_leader)
                serializer = GroupSerializer(group)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': '현재 그룹 리더가 아닙니다.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': '새로운 리더의 ID가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def set_edit(self, request, pk=None):
        group = self.get_object()
        
        if request.user == group.leader:
            group.set_edit(not group.editPer)
            serializer = GroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': '현재 그룹 리더가 아닙니다.'}, status=status.HTTP_403_FORBIDDEN)
  

    def perform_create(self, serializer):
        access_token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        try:
            decoded = jwt.decode(access_token, algorithms=['HS256'], verify=True, key=JWT_SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        
        user_id = decoded['userId']
        leader = User.objects.get(pk=user_id)
        serializer.save(leader=leader)

        serializer.instance.member.add(leader)

        return super().perform_create(serializer)
    
   
@permission_classes([IsAuthenticated])
class GroupListSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_queryset(self, **kwargs): # Override
        id = self.kwargs['userId']
        return self.queryset.filter(member=id)
    

class PlanViewSet(ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    permission_classes = [IsAuthenticated, IsGroupMember]

    def get_queryset(self, **kwargs): # Override
        if self.request.user.is_authenticated:    
            id = self.kwargs['groupId']
            return self.queryset.filter(group=id)
        
    def get_permissions(self):
        if self.action == 'create':
            group_id = self.request.data.get('group')
            group = get_object_or_404(Group, pk=group_id)

            if group.editPer:
                return [IsAuthenticated(), IsGroupMember()]
            else:
                return [IsAuthenticated(), IsGroupLeader()]
        return super().get_permissions()

    def perform_create(self, serializer):
        group_id = self.request.data.get('group')
        group = get_object_or_404(Group, pk=group_id)
        
        if group.member.filter(pk=self.request.user.pk).exists():
            if group.editPer or group.leader == self.request.user:
                serializer.save(group=group)
            elif not group.editPer:
                return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [IsAuthenticated, IsGroupMember]

    def get_queryset(self, **kwargs): # Override
        group_id = self.kwargs['groupId']
        plan_id = self.kwargs['planId']

        queryset = Category.objects.filter(
            plan__group__groupId=group_id,
            plan__planId=plan_id,
        )
        return queryset

    def get_permissions(self):
        if self.action == 'create':
            group_id = self.request.data.get('group')
            group = get_object_or_404(Group, pk=group_id)

            if group.editPer:
                return [IsAuthenticated(), IsGroupMember()]
            else:
                return [IsAuthenticated(), IsGroupLeader()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        group_id = self.request.data.get('group')
        plan_id = self.request.data.get('plan')

        group = get_object_or_404(Group, pk=group_id)
        plan = get_object_or_404(Plan, pk=plan_id, group=group)

        access_token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        try:
            decoded = jwt.decode(access_token, algorithms=['HS256'], verify=True, key=JWT_SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        user_id = decoded['userId']
        writer = User.objects.get(pk=user_id)

        serializer.save(plan=plan, writer=writer)
    
    def perform_update(self, serializer):
        group_id = self.kwargs['groupId']
        plan_id = self.kwargs['planId']

        group = get_object_or_404(Group, groupId=group_id)
        plan = get_object_or_404(Plan, pk=plan_id, group=group)

        category = get_object_or_404(
            Category,
            categoryId=self.kwargs['pk'],
            plan__group__groupId=group_id,
            plan__planId=plan_id,
        )

        if group.editPer or group.leader == self.request.user:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

from decouple import config

class ExchangeViewSet(ViewSet):

   # with open('apikey.json', 'r') as file:
       # api_key = json.load(file)['API_KEY']
    
    #api_key = os.environ.get("API_KEY")
    
    api_key = config('API_KEY')
    
    url="https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"

    def list(self, request):
        now = datetime.now()
        
        # 현재 시간이 11시 이전이면 전날로 변경하고 오후 6시로 설정
        if now.time() < time(11, 0, 0):
            now -= timedelta(days=1)
            now = now.replace(hour=18, minute=0, second=0, microsecond=0)

        # 주말인 경우 가장 최근의 금요일로 설정
        if now.weekday() == 5:  # 토요일
            days_to_friday = (now.weekday() - 4) % 7
            now -= timedelta(days=days_to_friday)
        elif now.weekday() == 6:  # 일요일
            days_to_friday = (now.weekday() - 4) % 7
            now -= timedelta(days=days_to_friday)


        current_date = now.strftime('%Y%m%d')

        params = {
        'authkey': self.api_key,
        'searchdate': current_date,
        'data':'AP01'
        }

        response=requests.get(self.url, params=params)
        r_data=response.json()
        
        if response.status_code == 200:
            exchange_data = response.json()
            if isinstance(exchange_data, list):
                
                exchange_info_list = []
                for exchange_info in exchange_data:
                    result = exchange_info.get('result')
                    curUnit = exchange_info.get('cur_unit')
                    curNm = exchange_info.get('cur_nm')
                    curNm = curNm.replace(" ", "-")
                    country_name = curNm.split('-')[0]
                    ttb = exchange_info.get('ttb')      # 외화를 구매할 때 적용하는 환율
                    tts = exchange_info.get('tts')      # 외화를 판매할 때 적용하는 환율
                    
                    if curUnit == "CNH":
                            country_name = "중국"
                            curNm = country_name + "-" + curNm
                    elif curUnit == "EUR":
                        country_name = "유럽연합"
                        curNm = country_name + "-" + curNm

                    exchange_info_list.append({
                        'result': result,
                        'curUnit': curUnit,
                        'curNm': curNm,
                        'country_name': country_name,
                        'ttb': ttb,
                        'tts': tts
                    })


                return Response(exchange_info_list)
            else:
                return Response({"error": "Exchange data not found."}, status=404)
        else:
            return Response({"error": "Request failed."}, status=400)


def generate_invite_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

class JoinGroupAPIView(APIView):
    serializer_class = JoinMemberSerializer
    
    def post(self, request):
        entered_invite_code = request.data.get('entered_invite_code', '')
        group = Group.objects.filter(invite_code=entered_invite_code).first()

        if group:
            user = request.user
            group.member.add(user)
            group.save()

            serializer = GroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid invite code'}, status=status.HTTP_400_BAD_REQUEST)


# class JoinGroupAPIView(APIView):
#     serializer_class = JoinMemberSerializer
    
#     def post(self, request):
#         entered_invite_code = request.data.get('entered_invite_code', '')

#         # 초대코드에 해당하는 그룹을 찾기
#         try:
#             group = Group.objects.get(invite_code=entered_invite_code)
#         except Group.DoesNotExist:
#             return Response({'message': 'Invalid invite code'}, status=status.HTTP_400_BAD_REQUEST)

#         user = request.user

#         # 사용자를 그룹에 추가
#         group.member.add(user)
#         group.save()

#         serializer = GroupSerializer(group)
#         return Response(serializer.data, status=status.HTTP_200_OK)

        
class InviteMembersAPIView(APIView):
    serializer_class = InviteMemberSerializer
    def post(self, request, group_id):
        group = get_object_or_404(Group, groupId=group_id)

        # 초대할 멤버의 이메일 가져오기
        invite_email = request.data.get('invite_email', '')

        if invite_email:
            # 그룹 모델의 invite_email 필드에 이메일 저장
            group.email = invite_email
            group.save_invited_email(invite_email)

            # 이메일로 초대코드 전송
            subject = '초대코드'
            message = f'여행가계 그룹에 초대되려면 다음 코드를 입력하세요: {group.invite_code}'
            from_email = 'yeohaenggagye@gmail.com'
            recipient_list = [invite_email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'Invitation sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

