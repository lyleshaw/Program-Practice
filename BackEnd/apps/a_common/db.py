from contextlib import contextmanager
from logging import getLogger

from sqlalchemy import func, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, Session

from apps.a_common.error import NotFound
from apps.foundation import SessionLocal

"""
约定
1. 所有varchar字段，都是用db.VARCHAR(126)，这样扩展强，性能消耗小（在PG SQL下）
2. 所有存外面的数据(比如OSS，NOSQL，文件系统）的变量，都用**_store_id
3. 所有的bool字段，变量名都为is_***
4. 所有时间字段，都用db.Integer
5. 尽量使用server_default，server_default=字符串。
6. 所有的ARRAY字段，变量名都为**_line
7. 所有的查询，都使用filter，而不使用filter_by
"""

logger = getLogger(__name__)
Base = declarative_base()


def flush_all(session, *args):
    """ add 0-n个ORM """
    if args:
        session.add_all(args)
        session.flush()


def flush(session: Session, instance):
    session.add(instance)
    session.flush()


def fast_count(query: Query) -> int:
    """
    原生的count有性能问题，这个函数对于大表的count会有很多性能提升
    """
    if query._group_by is not False:
        return query.session.query(query.subquery()).count() or 0
    
    total = query.session.execute(
        query.statement.with_only_columns([func.count()]).order_by(None)
    ).scalar()
    return total or 0  # total could be None


class Pagination:
    def __init__(self, query: Query, page_id=1, page_size=20, page_info=None):
        if page_info:
            page_id = page_info.page_id
            page_size = page_info.page_size
        
        if page_id < 1 or page_size < 1:
            logger.info(f'page_id: {page_id}, page_size: {page_size}, page_info: {page_info}')
            raise NotFound()
        
        total = fast_count(query)
        if total and total > 0:
            items = query.limit(page_size).offset((page_id - 1) * page_size).all()
        else:
            total = 0
            page_id = 1
            items = []
        
        self.items = items
        self.page_id = page_id
        self.page_size = page_size
        self.total = total
    
    @property
    def next_page_id(self):
        if self.page_id * self.page_size >= self.total:
            return None
        return self.page_id + 1
    
    @property
    def prev_page_id(self):
        if self.page_id == 1:
            return None
        return self.page_id - 1


# Dependency
async def get_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session_local() -> Session:
    """
    with get_session_local() as session:
        do_somethings()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def or_many_condition(condition: list):
    """ 有时候or能比in产生更好的性能，例如
    filter(or_many_condition([UserDB.id == i for i in user_ids]))
    会比
    filter(UserDB.id.in_(user_ids))
    性能更加好
    """
    if len(condition) == 0:
        return True
    
    if len(condition) == 1:
        return condition[0]
    
    return or_(*condition)


""" 生产动态表 暂时还没用 """
# class DynamicModelMixin(object):
# 	@classmethod
# 	def _create(cls, tb_suffix, auto_create_table=True):
# 		# 1.tb_suffix和cls，生成表名字
# 		# 2.搜索当前对象中的声明类是否有该类，如果有，直接使用其创建对象，否则尝试生成新类，创建数据库表并用新类创建对象
# 		# tb_keys = [cls.__name__.lower(), tb_suffix]
# 		# tb_name = '_'.join(filter(lambda x: x != '', tb_keys))
# 		tb_name = cls.__name__.lower()
# 		if tb_suffix != "":
# 			tb_name = "%s_%s" % (tb_name, str(tb_suffix))
# 		tb_cls = None
# 		if tb_name in db.Model._decl_class_registry:
# 			if isinstance(db.Model._decl_class_registry[tb_name], _MultipleClassMarker):
# 				tb_cls = list(db.Model._decl_class_registry[tb_name].contents)[0]()
# 			else:
# 				tb_cls = db.Model._decl_class_registry[tb_name]
# 		if tb_cls is None:
# 			if hasattr(cls, '__bind_key__'):
# 				db_engine = db.get_engine(bind=cls.__bind_key__)
# 			else:
# 				db_engine = db.get_engine()
# 			tb_exists = db_engine.dialect.has_table(db_engine, tb_name)
# 			if tb_exists or auto_create_table:
# 				metadata = {
# 					'__tablename__': tb_name,
# 					'__tb_suffix__': tb_suffix,
# 					'__table_args__': {
# 						'extend_existing': True
# 					}
# 				}
# 				tb_cls = type(tb_name, (db.Model, cls), metadata)
# 				if not tb_exists:
# 					tb_cls.__table__.create(bind=db_engine)
# 		return tb_cls
#
# 	@classmethod
# 	def check_on(cls):
# 		""" 检查一个动态表有没有on成具体的一个表 """
# 		table_name = getattr(cls, '__tablename__', None)
# 		if table_name is None:
# 			raise Exception('DynamicModel used before on')
# 		else:
# 			return table_name
#
# 	@classmethod
# 	def on(cls, suffix, auto_create_table=True):
# 		m = cls._create(suffix, auto_create_table)
# 		return m
#
# 	@classmethod
# 	def on_date(cls, suffix, date, auto_create_table=True):
# 		m = cls._create('{}_{}'.format(suffix, date), auto_create_table)
# 		return m

# def get_table_session(table):
# 	""" 获得对应表下的session """
# 	if getattr(table, '__bind_key__', None):
# 		engine = db.get_engine(bind=table.__bind_key__)
# 		session_maker = sessionmaker(engine)
# 		session = session_maker()
# 	else:
# 		session = db.sessionmaker()()
# 	return session
