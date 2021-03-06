# BBtree 

## Introduce
BBtree 뜻 : 베스트북을 나무의 열매처럼 모아 둔 공간입니다.<br>
회원제로 이루어지는 베스트셀러 도서 소개 웹 사이트 입니다. 

종합 베스트셀러 책들을 소개해 주고, 책에 관한 내용 확인과 댓글로 소통이 가능하며, 관심 도서 등록을 할 수 있습니다.

​
## Contributor

- @uuuuooii (김은혜)
- @duck9-papa (강인호)
- @Yoonwonsuh (서윤원)
- @tkrkr55 (김혜인) 
​

   
<br/><br/>

## Tech Requirement (Tech Stack)
- HTML5 / CSS3 /Javascript

- Python (flask / jinja2) 

- JWT 인증

- jQuery

- AWS

- MongoDB Atlas

<br/><br/>

## 페이지 별 기능
- 로그인
1. 로그인 기능
2. 회원 검사
3. ID/PW 입력 성공 시 메인 페이지로 이동
4. ID/PW 틀릴 alert 창 표시
5. '회원가입'버튼 클릭 시 회원가입 페이지로 이동
     
![로그인](/images/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202022-07-14%20%EC%98%A4%ED%9B%84%202.15.01.png)
<br/><br/>
- 회원가입
1. 회원가입 기능
2. 회원 가입 성공 시 로그인 페이지로 이동
<br/>

![회원가입](/images/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202022-07-14%20%EC%98%A4%ED%9B%84%202.15.17.png)
<br/>

---
<br/>

- 메인 페이지
1. 크롤링(스크래핑) 책 제목, 이미지, 순위 
2. 상위 20위 도서정보 스크래핑 후 도서정보 저장(교보문고 베스트셀러)
3. 선택한 도서 관심등록,취소 기능. 하트 버튼 누르면 관심 페이지로 정보가 담김.
4. 책 이미지 누르면 상세 페이지로 이동
<br/>

![메인페이지](/images/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202022-07-14%20%EC%98%A4%ED%9B%84%202.17.20.png)

---
<br/>


- 상세 페이지
1. 크롤링(스크래핑)책 세부 내용 (교보문고) 
2. 도서상세 정보 스크래핑
3. 댓글 리스트 작성 + 삭제 버튼으로 삭제 가능.
4. 내용 보기 버튼을 누르면 책 세부 내용이 나온다. 구매 페이지 누르면 교보문고 사이트로 이동한다.
<br/>

![상세페이지](/images/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202022-07-14%20%EC%98%A4%ED%9B%84%202.18.00.png)

---
<br/>


- 관심 페이지
1. 사용자가 관심등록한 도서목록을 카드 형식으로 표시
2. 사용자의 관심도서 하트 버튼 클릭 시 관심도서 목록에서 삭제 후 reload
<br/>

![관심페이지](/images/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202022-07-14%20%EC%98%A4%ED%9B%84%202.18.28.png)

---
2022.7.11~2.14