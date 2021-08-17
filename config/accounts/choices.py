SEOUL_DISTRICT_CHOICES = [
    #('FR', 'Freshman'), #DB에 저장하는 실제 값, display용 이름
    ('JONGNO', '종로구'), #이걸 동이랑 어떻게 연결??
    ('YONGSAN', '용산구'),
    ('SEOUNGDONG', '성동구'),
    ('GWANGJIN', '광진구'),
    ('DONGDAEMUN', '동대문구'),
    ('JUNGNANG', '중랑구'),
    ('SEONGBUK', '성북구'),
    ('GANGBUK', '강북구'),
    ('DOBONG', '도봉구'),
    ('NOWON', '노원구'),
    ('EUNPYEONG', '은평구'),
    ('SEODAEMUN', '서대문구'),
    ('MAPO', '마포구'),
    ('YANGCHEON', '양천구'),
    ('GANGSEO', '강서구'),
    #{'종로구': {'1동', '2동', '3동'}},

]

SEOUL_TOWN_CHOICES = [
    ('CHEONGUN', '청운효자동'),
    ('SAJIK', '사직동'),
    ('SAMCHEONG', '삼청동'),
    ('BUAM', '부암동'),
    ('PYEONGCHANG', '평창동'),
    ('MUAK', '무악동'),

]

DRINK_CHOICES=[
    ('americano', '아메리카노'),
    ('vanilla', '바닐라라떼'),
    ('cafelatte', '카페라떼'),
    ('caramel', '카라멜마끼아또'),
    ('choco', '초코라뗴'),
    ('ade', '에이드'),
    ('greentea', '녹차라떼'),
    ('herb', '허브차'),
    ('etc', '기타'),

]

EX_CAFE_LIST=[
    '뉴오리진 마포점',
    '스타벅스 마포용강동점',
    '개혁커피',
    '누룽지몰&카페',
    '카페273',
    '커피더맨',
    'KYO카페',
    '메종드아트',
    '라이브필카페',
    '가부커피 마포점',
    '달리는커피 서울염리초교점',
    '늘봄',
]

CITY_CHOICES=[
    ('서울특별시','서울특별시'),
]

GU_CHOICES=[
    ('종로구','종로구'),
    ('용산구','용산구'),
    ('성동구','성동구'),
    ('광진구','광진구'),
    ('중랑구','중랑구'),
    ('관악구','관악구'),

]

DONG_CHOICES=[
    ('청운효자동', '청운효자동'),
    ('사직동', '사직동'),
    ('삼청동', '삼청동'),
    ('부암동', '부암동'),
    ('평창동', '평창동'),
    ('무악동', '무악동'),
]