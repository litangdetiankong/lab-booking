from app.db.database import SessionLocal
from app.db.models import User
from app.core.security import hash_password

def main():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == "admin").first():
            print("admin 已存在，跳过")
            return 
        user = User(
            username="admin",
            password_hash=hash_password("123456"),
            nickname="管理员",
            role="admin",
        )
        db.add(user)
        db.commit()
        print(f"已创建测试用户 admin / 123456(id={user.id})")
    finally:
        db.close()

if __name__=="__main__":
    main()