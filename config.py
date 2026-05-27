"""
本文件为配置文件
需要注意的是,千万不要将带有真实API Key的文件上传到Github或截图
不过有懂Python的朋友也可以直接改为从环境变量或配置文件读取
除了main.py之外的文件都不应导入该文件

程序被设计为可以热重载配置文件
不过,需要注意的是:别手欠改完之后把自己锁外面了…
"""
SERVER_ADDRESS = 'http://ip:port'          # QQ端服务器的地址，请不要在最后一个字符加入斜杠或空格
CLIENT_ADDRESS = 'ip'                      # 监听地址
CLIENT_PORT = 114514                       # 监听端口

API_KEY = 'sk_123***'                      # AI的API Key
API_ADDRESS = 'https://api.deepseek.com/v1'#AI的API地址  很抱歉，目前只能使用纯文字，并不支持多模态
API_AI_MODEL = 'deepseek-chat'             # AI的模型
API_TEMPERATURE = 1.3                      # AI的温度，如不懂或是无此需要，无需修改
API_MAX_TOKENS = 4096                      # AI的最大输出量，请保证你清楚你在做什么后再修改，否则无需修改

OTA_ALLOW = False                          # OTA目前为测试状态，如果你不嫌可能会炸，那就可以试试
GITHUB_REPO = "bcht/Elaina"                # Github仓库地址，不要修改，除非你知道你在做什么，这很重要
BOT_QQ = 114514                            # 机器人QQ号
ADMIN = [114514]                           # 机器人管理员QQ，为保障安全，暂不支持直接修改
FORCE_JSON = False                         # 尝试使用更宽松的方式去判定json，若频繁出现解析错误，请调整为True，否则无需修改
PROMPT_MD = 'rs.md'                        # AI的提示词文件，默认使用md文件，且默认读取在程序根目录中。如需调整位置，请输入绝对路径

MESSAGE_UP = 50                            # 最高对话回合数
LOVE_UP = 100                              # 最高好感度
