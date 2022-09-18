
# ✨ KiraBot
# 소개
KiraBot은 한국의 학생 3명이 모여 만든 디스코드 봇입니다!<br>
급식 조회, 책 조회, 노래 재생, 로그 기록 등등.. 다양한 기능이 있으며,<br>
명령어는 ``빗금 명령어``로 사용 할 수 있어요!<br><br>

<a href="https://discord.com/api/oauth2/authorize?client_id=1011602097801809990&permissions=8&scope=applications.commands%20bot"><img width="100px" src="https://user-images.githubusercontent.com/68435966/187939033-005b1748-12d9-41e8-8e3b-8de047bbd0ae.png"/></a><br><br><br>

``✋ 다른 봇에서 본거같은 기능이 많은데, 이 봇은 왜 만들었나요?``<br><br>
다른 봇들에는 좋은 기능이 많습니다. 하지만, 그 좋은 기능이 여러 봇들에 나뉘어져 있는게 불편했고<br>
이 기능들을 합치고, 우리의 입맛에 맞게 만들어서 써보면 어떨까? 라는 생각에 이 봇을 만들게 되었습니다.


# 정보
**참여 인원** ``3명``<br>
<a href="https://github.com/oneseventh">@17th</a>, <a href="https://github.com/zzxz46412">@donggeon</a>, <a href="https://github.com/congachu">@congachu</a><br><br>
**사용 언어** ``Python``<br><br>
**사용 라이브러리** ``nextcord`` ``bs4`` ``yt_dlp``

노래봇에 [이 코드](https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d)를 참고 했어요!

# TODO

음악봇 명령어 버튼으로 대체 하기.
로그 채널 지정 명령어 버그 픽스


# 기능
<h2><a href="https://github.com/oneseventh">@17th</a> Part</h2><br>

<img src="https://user-images.githubusercontent.com/68435966/187944836-32a78b66-3174-43b8-8745-ec8689848a3a.png"/><br><br>
🎵 ``/join`` **- KiraBot이 보이스 채널에 입장 합니다.**<br>
🎵 ``/leave`` **- KiraBot이 보이스 채널에서 퇴장합니다. (퇴장과 동시에 대기열이 초기화 됩니다!)**<br>
🎵 ``/now`` **- 재생중인 노래의 정보를 표시 합니다.**<br>
🎵 ``/resume`` **- KiraBot이 멈춘 노래를 재생 합니다. [곧 버튼으로 대체될 예정 입니다!]**<br>
🎵 ``/pause`` **- KiraBot이 재생중인 노래를 멈춥니다. [곧 버튼으로 대체될 예정 입니다!]**<br>
<br><img src="https://user-images.githubusercontent.com/68435966/187945605-85cb9f52-58aa-4f4f-9974-ff976f512b3c.png"/><br><br>
🎵 ``/queue`` **- KiraBot이 예약된 노래 목록을 표시합니다.**<br>
🎵 ``/skip`` **- KiraBot이 재생중인 노래를 스킵 합니다.**<br>
🎵 ``/remove [index]`` **- KiraBot이 대기열에서 index 노래를 삭제합니다.**<br>
🎵 ``/play [url or keyword]`` **- KiraBot이 노래를 재생 합니다. 만약, 재생중인 노래가 있다면 대기열에 추가 시킵니다.**<br>
<br><img src="https://user-images.githubusercontent.com/68435966/187948224-cf9f3d75-cc0d-4d9e-9e6a-d71447d1fbb6.png"/><br><br>
📝 ``/memo [읽기 or 쓰기]`` **- 메모를 작성하거나 읽을 수 있습니다. (메모는 서버가 아닌, 전체 공유 입니다.)**<br><br>
<br><img src="https://user-images.githubusercontent.com/68435966/187947251-b3372e49-6009-48dd-99b9-b656503b2926.png"/><br><br>
🍔 ``/meal [date] [school]`` **- 급식을 확인 합니다.**<br><br>
<br><img src="https://user-images.githubusercontent.com/68435966/187946824-6a25b714-d72f-4d90-b043-5a76a5a3cab6.png"/><br><br>
📖 ``/search [book_name] [page]`` **- 책을 검색 합니다.**<br><br>

<h2><a href="https://github.com/zzxz46412">@donggeon</a> Part</h2><br>

📖 ``/로그 [channel]`` **채팅에 대한 로그를 적어둘 채널을 설정합니다.**<br>
   - 아래 사진과 같이 채팅에 대한 로그를 볼 수 있습니다. (메세지 수정, 삭제, 채널이동, 역할업데이트, 역할생성, 초대코드 등등)
<br><img src="https://user-images.githubusercontent.com/80456015/190886902-739048f8-77a8-4773-ab44-cff0a9877277.png"/><br><br>


<h2><a href="https://github.com/congachu">@congachu</a> Part</h2><br>


![clean](https://user-images.githubusercontent.com/106534469/187964960-605038ac-d3d5-4caa-8f48-f7e0cd915f1c.png)<br><br>
🧹 ``/청소 [number]`` - **최대 99개**의 채팅을 청소합니다.<br><br><br>

![NICK](https://user-images.githubusercontent.com/106534469/187964991-d554f080-ac5b-4531-a06d-1dcfab99fbb9.png)<br><br>
🔁 ``/닉변 [mention] [name]`` - **자신의 이름** 또는 **서버 구성원의 닉네임**을 변경합니다.<br><br><br>

![say](https://user-images.githubusercontent.com/106534469/187965002-b2d471c6-0ae8-44be-a452-026785c96428.PNG)<br><br>
💬 ``/따라해 [text]`` - 봇이 단어를 따라 말합니다<br><br><br>

![gamble](https://user-images.githubusercontent.com/106534469/187964970-d486cecc-cf69-4e90-9328-fa683a8fd39b.png)<br><br>
🎲 ``/홀짝 [홀/짝]`` - **반반 확률**로 홀 또는 짝이 나옵니다.<br><br><br>

![league](https://user-images.githubusercontent.com/106534469/187964979-2c8588e9-e4c3-4f79-8d22-6730699f9d80.PNG)<br><br>
🏆 ``/대회 인기`` - 현재 인기있는 대회, 공모전을 보여줍니다.<br>
🏆 ``/대회 추천`` - 추천하고 싶은 대회, 공모전을 보여줍니다.<br>
🏆 ``/대회 최신`` - 최근에 올라온 대회, 공모전을 보여줍니다.<br>
🏆 ``/대회 전체`` - 위 항목을 모두 보여줍니다.<br><br><br>
