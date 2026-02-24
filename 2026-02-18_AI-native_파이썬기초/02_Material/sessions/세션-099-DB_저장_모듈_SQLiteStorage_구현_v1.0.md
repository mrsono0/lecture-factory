# 세션 099: DB 저장 모듈(SQLiteStorage) 구현

| 항목 | 값 |
|------|-----|
| **세션 ID** | MS-PY101-099 |
| **소요 시간** | 25분 |
| **난이도** | ★★☆ (medium) |
| **청크 타입** | code |
| **선행 세션** | 098 (필수) |
| **학습 목표** | `sqlite3` 모듈을 활용하여 고객 데이터를 SQLite 데이터베이스에 저장하고 불러오는 `SQLiteStorage` 클래스를 구현할 수 있다 |
| **출처** | [Source A] 8 코딩.pdf §8.14 데이터 영속화 · [Source B] day5_notebooklm.md · [Source C] day5_deep_research.md |

---

## ① 도입 — "종이 장부의 한계"

🗣️ 강사 대본 (Instructor Script):

여러분, 지난 세션에서 JSON 파일로 데이터를 저장하는 데 성공했습니다. 프로그램을 껐다 켜도 데이터가 살아남죠. 하지만 한 가지 상상을 해 봅시다. 고객이 100만 명이 되면 어떨까요? `customers.json` 파일 하나에 100만 건의 데이터가 들어 있으면, "홍길동"이라는 고객을 찾으려면 파일 전체를 처음부터 끝까지 읽어야 합니다. 종이 장부에서 이름을 하나하나 눈으로 훑는 것과 같아요. 이것은 비효율의 극치입니다. 오늘은 이 한계를 극복하는 두 번째 저장소, 데이터베이스(DB)를 만나 보겠습니다.

---

## ② 비유 — 종이 장부 vs 전산 시스템

🗣️ 강사 대본 (Instructor Script):

비유를 들어 볼게요 [Source A][Source B]. JSON 파일 저장은 종이 장부와 같습니다. 모든 고객 정보가 한 권의 노트에 순서대로 적혀 있어요. 찾으려면 첫 페이지부터 넘겨야 합니다. 반면 데이터베이스는 전산 시스템입니다. 컴퓨터에 "홍길동 찾아줘"라고 입력하면 0.001초 만에 결과가 나옵니다. 인덱스(색인)라는 기술 덕분에 100만 건이든 1,000만 건이든 검색 속도가 거의 일정합니다.

파이썬에는 `sqlite3`라는 내장 데이터베이스가 있습니다 [Source C]. 별도의 서버 설치 없이, `import sqlite3` 한 줄이면 바로 사용할 수 있습니다. 데이터는 `.db` 확장자의 파일 하나에 저장되며, SQL(Structured Query Language)이라는 표준 언어로 데이터를 조작합니다. SQL은 "SELECT * FROM customers WHERE name = '홍길동'"처럼 영어 문장에 가까운 직관적인 문법을 가지고 있어서, 프로그래밍 초보자도 금방 익힐 수 있습니다.

---

## ③ 개념 설명 — SQLite와 SQL 기초

🗣️ 강사 대본 (Instructor Script):

SQL의 핵심 명령어 네 가지만 알면 됩니다 [Source A][Source C]. `CREATE TABLE`은 테이블(표)을 만들고, `INSERT INTO`는 데이터를 넣고, `SELECT`는 데이터를 조회하고, `DELETE`는 데이터를 삭제합니다. 우리의 CRUD와 정확히 대응되죠 — Create(INSERT), Read(SELECT), Update(UPDATE), Delete(DELETE).

`sqlite3` 모듈의 사용 패턴은 세 단계입니다. 첫째, `sqlite3.connect("파일명.db")`로 연결합니다. 둘째, `cursor`를 만들어 SQL 명령을 실행합니다. 셋째, `conn.commit()`으로 변경사항을 확정하고, `conn.close()`로 연결을 닫습니다.

---

## ④ 코드 — SQLiteStorage 구현

🗣️ 강사 대본 (Instructor Script):

코드를 봅시다.

```python
import sqlite3

class SQLiteStorage(Storage):
    def __init__(self, db_path: str = "customers.db"):
        self._db_path = db_path
        self._create_table()

    def _create_table(self) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, customers: list[Customer]) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute("DELETE FROM customers")  # 기존 데이터 초기화
        for c in customers:
            conn.execute(
                "INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)",
                (c.name, c.phone, c.email)
            )
        conn.commit()
        conn.close()
        print(f"✅ {len(customers)}명의 고객 데이터를 DB에 저장했습니다.")

    def load(self) -> list[Customer]:
        conn = sqlite3.connect(self._db_path)
        rows = conn.execute("SELECT name, phone, email FROM customers").fetchall()
        conn.close()
        return [Customer(name=r[0], phone=r[1], email=r[2]) for r in rows]
```

핵심을 짚겠습니다. `_create_table()`은 테이블이 없으면 새로 만듭니다. `save()`에서 `?`는 SQL 인젝션 공격을 방지하는 플레이스홀더입니다 — 값을 직접 문자열에 넣지 않고 튜플로 전달합니다. `load()`에서 `fetchall()`은 모든 행을 리스트로 가져옵니다.

🎙️ 실습 가이드 (Lab Guide):

AI에게 이렇게 요청하세요. "Storage 클래스를 상속받아 SQLiteStorage를 구현해줘. sqlite3 모듈을 사용해서 Customer 데이터를 DB에 저장하고 불러오는 기능을 만들어줘." 생성된 코드를 실행하고, 고객 3명을 등록한 뒤 `save()`를 호출해 보세요. 프로젝트 폴더에 `customers.db` 파일이 생성되었는지 확인합니다.

---

## ⑤ 정리 — "전산 시스템 도입 완료"

🗣️ 강사 대본 (Instructor Script):

이제 두 가지 저장소가 준비되었습니다. 종이 장부(`JsonFileStorage`)와 전산 시스템(`SQLiteStorage`). 둘 다 `Storage`라는 같은 약속(인터페이스)을 지키고 있으니, `CustomerManager`에 어떤 것을 넣어줘도 동작합니다. 다음 세션에서는 이 두 저장소를 실제로 갈아 끼워 보면서, DI의 진정한 위력을 체험하겠습니다!
