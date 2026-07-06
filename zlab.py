# a="nguyen_minh_quan".replace("_", " ")
# print(a)
# print(a=="nguyen minh quan")

import random
random.seed(42)
users = []
last_names = [
    "Nguyễn",
    "Trần",
    "Lê",
    "Phạm",
    "Huỳnh",
    "Phan",
    "Hoàng",
    "Võ"
]
middle_names = [
    "Văn",
    "Thị",
    "Minh",
    "Ngọc",
    "Đăng",
    "Anh",
    "Gia"
]
SAMPLE_NAMES = [
    "An","Bình","Chi","Duy","Em","Phong","Giang","Hà","Ivy","Khánh",
    "Lan","Minh","Nam","Oanh","Quang","Sơn","Trang","Tuấn","Vy","Yến"
]

while True:
    fullname = "{} {} {}".format(
        random.choice(last_names),
        random.choice(middle_names),
        random.choice(SAMPLE_NAMES)
    )
    print(fullname)
    test=input("").replace("_", " ")
    print(test in fullname)

