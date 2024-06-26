![Network Topology](sample/DALLE_hhji_20240408_Create_a_detailed_illustration_of_a_fully_connected.webp)
- Image create by DALLE_hhji ( 20240408 )

##
## [ 파일설명 ]
### 1. (최초) 실행전 파일: 3개 ( 윈도우환경 )
  - netstat.sh : 서버내에서 체크할 스크립트명령
  - name_map.conf : 주요설정파일 ( ssh접속할 인스턴스 필수입력 )
  - netstat_v?.?.?.exe : ( 위 설정파일 읽어서 접속해서 스크립트 전송후 실행, 결과 취합해서 네트워크 토폴로지 그림1장 그린다. )

### 2. (실행후) 결과 파일 : 2개
  - netstat.log : 인스턴스별 netstat 명령 실행결과 로그
  - netstat_{CurrentTime}.png : 네트워크 토폴로지 그림 ( 위 로그파일 첫줄에 체크시간을 우측하단에 표기함 )

### 3. 맥 에서는 컴파일후 신뢰할수없는 없다고하여, 아래 개발환경 구성해서 netstat_dev_v?.?.?.py 실행해주세요
  - 개발환경: New Macbook 2017, Intel I5 1.3Ghz, Python3.12.2
  - 라이브러리 : requirements.txt
    - matplotlib networkx paramiko scp getpass configparser

##
## [ netstat.sh ]

### 1. 목적/역할
서버에 SSH로 접속하여 `netstat` 명령을 실행하는 스크립트입니다. 정규식과 조건들 때문에 소스 코드 내부가 아닌 별도의 스크립트로 작성하였습니다.

### 2. 변수 설정
- **Number_Of_HighLine**
  - `netstat` 스크립트는 연결이 많은 것부터 상위에 정렬합니다. 이 변수는 상위 몇 개의 라인을 표시할지 결정합니다.
  - 기본값은 3입니다. 값이 클수록 화면에 많은 정보가 표시되어 복잡해질 수 있습니다.

##
## [ name_map.conf ]

### 1. 한글 사용 제한
한글 주석을 사용하면 인코딩 에러로 인해 파일을 읽지 못할 수 있습니다.

### 2. 섹션별 설명
#### 2.1 [port_service_map]
- 포트 번호를 서비스 명으로 매핑합니다.

#### 2.2 [dns_name_map]
- IP 주소를 도메인 명으로 매핑합니다.

#### 2.3 [instance_map]
- 체크할 인스턴스 목록입니다. 
  - SSH 접속 후 `netstat` 실행하여 로그에 결과를 취합합니다. 아이디와 비밀번호는 처음에 입력받습니다.
  - 예) `192.168.0.2` = `192-168-0-2`

#### 2.4 [draw_options]
- 그래픽 옵션 설명
  - **node**: 서버를 동그라미로 표시
  - **edge**: 서버 간의 통신을 선으로 연결
  - **arrow**: 통신의 방향성을 화살표로 표시 (수신 서버 = 화살표 받은 것, 송신 서버 = 화살표 보낸 것)
  - **connectionstyle**: 화살표의 스타일 결정
    - `arc3`, `arc`: 부드러운 곡선으로 연결
    - `angle3`, `angle`: 각진 선분으로 연결
    - `bar`: 수직 막대로 연결
    - `round`: 둥근 선분으로 연결
