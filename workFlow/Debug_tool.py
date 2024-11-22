def Check_input_output(func):
    def _warpper(*args,**kwargs):
        print("input:---------------------------")
        for arg in args:
            print(arg)
            print('*'*120)
        print(kwargs)

        result = func(*args,**kwargs)

        print("output:---------------------------")
        print("結果:",result)
        return result
    return _warpper