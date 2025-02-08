# localization.py

MESSAGES = {
    "en": {
        "greeting": "Hello! Welcome to the app for international students.",
        "choose_language": "Please choose your language:",
        "enter_login": "Please enter your login (nickname):",
        "invalid_login": "Invalid login. Please use only English letters, numbers, and underscores.",
        "enter_password": "Please enter your password:",
        "enter_city": "In which city do you live?",
        "choose_university": "Which university do you study at?",
        "university_auth": ("To link your university account, please click the link: "
                            "<a href='https://university-auth.example.com'>Authorize your university account</a>. "
                            "Authorization will finish in 3 seconds. This is an example of how the university account login will be structured to obtain the schedule."),
        "registration_finished": "Registration complete. Your schedule has been received. Please choose an action:",
        "event_search": "Search events",
        "update_info": "Supplement information about yourself",
        "edit_schedule": "Edit schedule",
        "view_schedule": "My schedule",
        "already_registered": "You are already registered.",
        "enter_activity": "On a scale of 1 to 5, how <b>active</b> are you?",
        "enter_sociability": "On a scale of 1 to 5, how <b>sociable</b> are you?",
        "enter_hobbies": "Please describe what you like:",
        "update_enter_activity": "On a scale of 1 to 5, how <b>active</b> are you?",
        "update_enter_sociability": "On a scale of 1 to 5, how <b>sociable</b> are you?",
        "update_enter_hobbies": "Please describe what you enjoy:",
        "info_updated": "Information updated.",
        "edit_schedule_prompt": ("Enter an event in the format: [day] [start time] - [end time] [event description]\n"
                                 "Example: MN 19:40 - 21:30 Movie screening")
    },
    "ru": {
        "greeting": "Привет! Добро пожаловать в приложение для иностранных студентов.",
        "choose_language": "Пожалуйста, выберите язык:",
        "enter_login": "Введите, пожалуйста, ваш логин (никнейм):",
        "invalid_login": "Некорректный логин. Пожалуйста, используйте только английские буквы, цифры и символы подчеркивания.",
        "enter_password": "Введите, пожалуйста, ваш пароль:",
        "enter_city": "В каком городе вы живёте?",
        "choose_university": "В каком вузе вы учитесь?",
        "university_auth": ("Для привязки учётной записи вуза, пожалуйста, нажмите на ссылку: "
                            "<a href='https://university-auth.example.com'>Авторизоваться</a>. "
                            "Через 3 секунды авторизация закончится, и это пример как будет устроен вход в учётную запись вуза для получения расписания."),
        "registration_finished": "Регистрация завершена. Ваше расписание получено. Пожалуйста, выберите действие:",
        "event_search": "Поиск события",
        "update_info": "Дополнить информацию о себе",
        "edit_schedule": "Внести правки в расписание",
        "view_schedule": "Мое расписание",
        "already_registered": "Вы уже зарегистрированы.",
        "enter_activity": "По шкале от 1 до 5, насколько <b>активный</b> вы?",
        "enter_sociability": "По шкале от 1 до 5, насколько <b>общительный</b> вы?",
        "enter_hobbies": "Расскажите, что вам нравится:",
        "update_enter_activity": "По шкале от 1 до 5, насколько <b>активный</b> вы?",
        "update_enter_sociability": "По шкале от 1 до 5, насколько <b>общительный</b> вы?",
        "update_enter_hobbies": "Опишите, что вам нравится:",
        "info_updated": "Информация обновлена.",
        "edit_schedule_prompt": ("Введите событие в формате: [день недели] [время начала] - [время конца] [событие]\n"
                                 "Пример: ПН 19:40 - 21:30 просмотр фильма")
    },
    "be": {
        "greeting": "Прывітанне! Сардэчна запрашаем у прыкладанне для замежных студэнтаў.",
        "choose_language": "Калі ласка, абярыце мову:",
        "enter_login": "Увядзіце, калі ласка, ваш лагін (нік):",
        "invalid_login": "Некарэктны лагін. Калі ласка, выкарыстоўвайце толькі лацінскія літары, лічбы і сімвалы падкрэслення.",
        "enter_password": "Увядзіце, калі ласка, ваш пароль:",
        "enter_city": "У якім горадзе вы жывяце?",
        "choose_university": "У якім універсітэце вы вучыцеся?",
        "university_auth": ("Для прывязкі ўліковага запісу ўніверсітэта, калі ласка, націсніце на спасылку: "
                            "<a href='https://university-auth.example.com'>Аўтарызавацца</a>. "
                            "Праз 3 секунды аўтарызацыя скончыцца, і гэта прыклад таго, як будзе арганізаваны ўваход у ўліковы запіс універсітэта для атрымання раскладу."),
        "registration_finished": "Рэгістрацыя завершана. Ваш расклад атрыманы. Калі ласка, абярыце дзеянне:",
        "event_search": "Пошук мерапрыемстваў",
        "update_info": "Дапоўніць інфармацыю пра сябе",
        "edit_schedule": "Унесці папраўкі ў расклад",
        "view_schedule": "Маё расклад",
        "already_registered": "Вы ўжо зарэгістраваны.",
        "enter_activity": "Па шкале ад 1 да 5, наколькі <b>актыўны</b> вы?",
        "enter_sociability": "Па шкале ад 1 да 5, наколькі <b>камунікатыўны</b> вы?",
        "enter_hobbies": "Раскажыце, што вам падабаецца:",
        "update_enter_activity": "Па шкале ад 1 да 5, наколькі <b>актыўны</b> вы?",
        "update_enter_sociability": "Па шкале ад 1 да 5, наколькі <b>камунікатыўны</b> вы?",
        "update_enter_hobbies": "Апішыце, што вам падабаецца:",
        "info_updated": "Інфармацыя абноўлена.",
        "edit_schedule_prompt": ("Увядзіце падзею ў фармаце: [дзень тыдня] [час пачатку] - [час заканчэння] [падзея]\n"
                                 "Прыклад: ПН 19:40 - 21:30 прагляд фільма")
    },
    "kk": {
        "greeting": "Сәлем! Шетел студенттеріне арналған қосымшаға қош келдіңіз.",
        "choose_language": "Тіл таңдаңыз:",
        "enter_login": "Логинді (никнейм) енгізіңіз:",
        "invalid_login": "Жарамсыз логин. Тек ағылшын әріптері, сандар және астын сызу белгісін қолданыңыз.",
        "enter_password": "Құпия сөзді енгізіңіз:",
        "enter_city": "Сіз қай қалада тұрасыз?",
        "choose_university": "Сіз қай университетте оқисыз?",
        "university_auth": ("Университеттегі есептік жазбаны байланыстыру үшін, өтінеміз, сілтемеге өтіңіз: "
                            "<a href='https://university-auth.example.com'>Авторизация</a>. "
                            "3 секундтан кейін авторизация аяқталады, және бұл сіздің университеттік кестеңізді алу үшін университеттік есептік жазбаға кірудің үлгісі болып табылады."),
        "registration_finished": "Тіркеу аяқталды. Сіздің кестеңіз алынды. Өтінеміз, әрекетті таңдаңыз:",
        "event_search": "Іс-шараларды іздеу",
        "update_info": "Өзіңіз туралы ақпаратты толықтыру",
        "edit_schedule": "Кестеге түзету енгізу",
        "view_schedule": "Менің кестем",
        "already_registered": "Сіз бұрын тіркелгенсіз.",
        "enter_activity": "1-ден 5-ке дейінгі шкала бойынша, сіз қаншалықты <b>белсенді</b>сіз?",
        "enter_sociability": "1-ден 5-ке дейінгі шкала бойынша, сіз қаншалықты <b>ашық</b>сыз?",
        "enter_hobbies": "Сізге не ұнайтынын айтыңыз:",
        "update_enter_activity": "1-ден 5-ке дейінгі шкала бойынша, сіз қаншалықты <b>белсенді</b>сіз?",
        "update_enter_sociability": "1-ден 5-ке дейінгі шкала бойынша, сіз қаншалықты <b>ашық</b>сыз?",
        "update_enter_hobbies": "Сипаттаңыз, сізге не ұнайды:",
        "info_updated": "Ақпарат жаңартылды.",
        "edit_schedule_prompt": ("Оқиғаны келесі форматта енгізіңіз: [апта күні] [басталу уақыты] - [аяқталу уақыты] [оқиға]\n"
                                 "Мысал: ДҰ 19:40 - 21:30 кино көру")
    },
    "zh": {
        "greeting": "你好！欢迎使用针对国际学生的应用程序。",
        "choose_language": "请选择你的语言：",
        "enter_login": "请输入您的登录名（昵称）：",
        "invalid_login": "无效的登录名。请只使用英文字母、数字和下划线。",
        "enter_password": "请输入您的密码：",
        "enter_city": "您居住在哪个城市？",
        "choose_university": "您在哪个大学就读？",
        "university_auth": ("要关联您的大学账户，请点击链接：<a href='https://university-auth.example.com'>授权您的大学账户</a>。"
                            " 3秒后，授权将结束，这是一个示例，展示如何通过大学账户登录以获取时间表。"),
        "registration_finished": "注册完成。您的时间表已收到。请选择一个操作：",
        "event_search": "搜索活动",
        "update_info": "补充个人信息",
        "edit_schedule": "修改时间表",
        "view_schedule": "我的时间表",
        "already_registered": "您已注册。",
        "enter_activity": "在1到5的范围内，您觉得自己有多<b>活跃</b>？",
        "enter_sociability": "在1到5的范围内，您觉得自己有多<b>社交</b>？",
        "enter_hobbies": "请描述您喜欢的内容：",
        "update_enter_activity": "在1到5的范围内，您觉得自己有多<b>活跃</b>？",
        "update_enter_sociability": "在1到5的范围内，您觉得自己有多<b>社交</b>？",
        "update_enter_hobbies": "请描述您喜欢的事物：",
        "info_updated": "信息已更新.",
        "edit_schedule_prompt": ("请输入事件，格式为：[星期缩写] [开始时间] - [结束时间] [事件描述]\n"
                                 "例如：周一 19:40 - 21:30 观看电影")
    },
    "ko": {
        "greeting": "안녕하세요! 국제 학생들을 위한 앱에 오신 것을 환영합니다.",
        "choose_language": "언어를 선택해주세요:",
        "enter_login": "로그인(닉네임)을 입력해주세요:",
        "invalid_login": "잘못된 로그인입니다. 영어 문자, 숫자, 밑줄만 사용해주세요.",
        "enter_password": "비밀번호를 입력해주세요:",
        "enter_city": "어느 도시에 사시나요?",
        "choose_university": "어느 대학교에 다니시나요?",
        "university_auth": ("대학교 계정을 연결하려면 아래 링크를 클릭해주세요: <a href='https://university-auth.example.com'>인증하기</a>. "
                            "3초 후에 인증이 종료됩니다. 이는 시간표를 받기 위해 대학교 계정으로 로그인하는 방법의 예제입니다."),
        "registration_finished": "등록이 완료되었습니다. 시간표가 수신되었습니다. 행동을 선택해주세요:",
        "event_search": "이벤트 검색",
        "update_info": "자신의 정보를 보완하기",
        "edit_schedule": "시간표 수정",
        "view_schedule": "내 시간표",
        "already_registered": "이미 등록되어 있습니다.",
        "enter_activity": "1부터 5까지의 척도에서, 얼마나 <b>활발한</b> 편이신가요?",
        "enter_sociability": "1부터 5까지의 척도에서, 얼마나 <b>사교적인</b> 편이신가요?",
        "enter_hobbies": "좋아하는 것을 설명해주세요:",
        "update_enter_activity": "1부터 5까지의 척도에서, 얼마나 <b>활발한</b> 편이신가요?",
        "update_enter_sociability": "1부터 5까지의 척도에서, 얼마나 <b>사교적인</b> 편이신가요?",
        "update_enter_hobbies": "좋아하는 것을 설명해주세요:",
        "info_updated": "정보가 업데이트되었습니다.",
        "edit_schedule_prompt": ("[요일] [시작 시간] - [종료 시간] [이벤트 설명] 형식으로 이벤트를 입력해주세요.\n"
                                 "예: 월 19:40 - 21:30 영화 감상")
    }
}

LANG_MAP = {
    "lang_ru": "ru",
    "lang_en": "en",
    "lang_be": "be",
    "lang_kk": "kk",
    "lang_zh": "zh",
    "lang_ko": "ko"
}

def get_msg(lang: str, key: str) -> str:
    return MESSAGES.get(lang, MESSAGES["en"]).get(key, "")
