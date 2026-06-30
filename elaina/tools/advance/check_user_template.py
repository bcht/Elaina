user_template = {#用户文件模版
    "message":[],#消息，包括用户和机器人的
    "favor":0,#好感度
    "time":[]
}

def is_user_template_complete(data : dict ) -> bool:#用于检查传入的字典是否符合规范
    """
    输入  
    data->dict  
    输出  
    bool  
    用于检查用户信息是否符合模版，返回True表示符合模版，返回False表示不符合模版  
    防呆不防傻，只要我不傻，并且用这个，估计就没毛病  
    """
    # 必需键集合
    required_keys = {"message", "favor", "time"}
    # 检查键是否存在
    if not all(key in data for key in required_keys):
        return False
    # 检查值的类型
    type_checks = {
        "message": list,
        "favor": int,
        "time": list
    }
    for key, expected_type in type_checks.items():#挨个检查  #将样本转换为可遍历的类型
        if not isinstance(data[key], expected_type):#判断是否为当前的类型
            return False
    return True