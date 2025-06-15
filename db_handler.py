from models import Activity, SessionLocal, init_db
import json

def save_activities_to_db(activities):
    session = SessionLocal()
    try:
        for act in activities:
            # 唯一性校验：url
            db_obj = session.query(Activity).filter_by(url=act.get("url")).first()
            if db_obj:
                # 已存在，更新字段
                for k, v in act.items():
                    if k == "tags" and isinstance(v, list):
                        v = json.dumps(v)
                    setattr(db_obj, k, v)
            else:
                # 不存在，插入新纪录
                session.add(Activity(**act))
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"落库失败: {e}")
    finally:
        session.close() 