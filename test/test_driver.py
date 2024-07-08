from __future__ import print_function
import os
import sys
import json
import time
import datetime
from datetime import timedelta
import re
if __name__ != "__main__":
    configpath= 'C:\mos-system-tests\Test\TestProject\Config\set_data\script_info.json'
    with open(configpath, 'r') as file :
        jsonData = json.load(file)
        python_file_path = jsonData["path"]["python_path"]
        project_file_path = jsonData["path"]["project_path"]
        csv_file_path = jsonData["path"]["csv_path"]
    sys.path.insert(0,python_file_path)
    import log_tool
    log_tool.DEBUG_MODE = True


def make_function_name( type_name, name ):
    function_name = type_name + '_' + name
    return function_name
    
    
def log_print(log_text, pou_data = None):
    if pou_data != None:
        pou_data.add_log( log_text )
        return
    print(log_text)
    log_tool.put_log(log_text)

CODESYS_FUNC = """

FUNCTION ShowAlertDialog(message)
VAR
    bOkPressed: BOOL;
BEGIN
    bOkPressed := INFO('Alert', message, BUTTONS_YES_NO) = BUTTON1_YES;
END_FUNCTION

FUNCTION ResultLog( message )
VAR
    SysLog(LOG_ERROR, message);
"""
def date_string_to_int(date_str):
    date_str = date_str.replace("DATE#", "")
    date_str = date_str.split( "-")
    result = int( date_str[0] )*10000 + int(date_str[1]) * 100 + int(date_str[2])

    return result

def time_string_to_timedelta(time_str):
    time_str = time_str.replace("TIME#", "")
    pattern = r'((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?'
    match = re.match(pattern, time_str)
    if match:
        days = int(match.group('days') or 0)
        hours = int(match.group('hours') or 0)
        minutes = int(match.group('minutes') or 0)
        seconds = int(match.group('seconds') or 0)
        milliseconds = int(match.group('milliseconds') or 0)
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
    else:
        raise ValueError("Invalid time format")

def text_value_check_type(type_text,value_text,min_value,max_value=None):
    if( max_value==None ):
        max_value = min_value
    
    result = False
    if type_text == "INT":
        result_value = int(value_text)
        result = (int(min_value)<= result_value and result_value <=int( max_value))
    elif type_text == "UINT":
        result_value = int(value_text)
        result = (int(min_value)<= result_value and result_value <=int( max_value))
    elif type_text == "ULINT":
        result_value = int(value_text)
        result = (int(min_value)<= result_value and result_value <=int( max_value))
    elif type_text == "WORD":
        result_value = int(value_text)
        result = (int(min_value)<= result_value and result_value <=int( max_value))
    elif type_text == "REAL":
        result_value = float(value_text)
        result = (float(min_value)<= result_value and result_value <=float( max_value))
    elif type_text == "STRING":
        result_value = str(value_text)
        result = (str(min_value)<= result_value and result_value <=str( max_value))
    elif type_text == "DATE":
        result_value = date_string_to_int(value_text)
        result = (date_string_to_int(min_value)<= result_value and result_value <=date_string_to_int( max_value))
    elif type_text == "TIME":
        result_value = time_string_to_timedelta(value_text)
        result = (time_string_to_timedelta(min_value)<= result_value and result_value <=time_string_to_timedelta( max_value))
    elif type_text == "BYTE":
        result_value = int(value_text)
        # log_print( "byte:"+number)
        result = int(min_value)<= result_value and result_value <=int( max_value)
        log_print( 'min=%s:max=%s:result=%s'%(str(min_value),str(max_value),str(result)))
    elif type_text == "BOOL":
        result_value = str(value_text)
        result = (str(min_value)<= result_value and result_value <=str( max_value))
    else:
        result_value =(value_text)

    return result
    
def string_to_typevalue( type_value_text ):
    if type_value_text == "TRUE":
        return "BOOL","TRUE"
    if type_value_text  == "FALSE":
        return "BOOL","FALSE"
    type_value_text = type_value_text.replace("'", "")
    parts = type_value_text .split('#')
    if len( parts ) <= 1:
        parts[0] = parts[0].replace( "\r", "")
        parts[0] = parts[0].replace( "\n", "")


        return "STRING",parts[0]

    type_text = parts[0]
    value_text = parts[1]
    return type_text,value_text
    
def text_value_check(value_text,min_value,max_value):
    if min_value=="TRUE" and value_text == "TRUE":
        return True
    if min_value=="FALSE" and value_text == "FALSE":
        return True

    if __name__=="__main__":
        if min_value == "":
            return True
        
    parts = value_text.split('#')
    if len( parts ) <= 1:
        parts[0] = parts[0].replace( "'", "")
        parts[0] = parts[0].replace( "\r", "")
        parts[0] = parts[0].replace( "\n", "")
        min_value = min_value.replace( "'", "")
        min_value = min_value.replace( "\n", "")
        min_value = min_value.replace( "'", "")
        min_value = min_value.replace( "\r", "")

        result = parts[0] == min_value
        return result

    type_text = parts[0]
    value_text = parts[1]
    result = False

    result = text_value_check_type(type_text,value_text,min_value,max_value)

    return result

class Variable:
    def __init__(self, var_type, name, init_value, min_value, max_value):
        self.name = name
        self.var_type = var_type
        self.init_value = init_value
        self.min_value = min_value
        self.max_value = max_value
        self.result = 0.0


    def init_statement(self):
        line = '%s : %s := %s ;' % (self.name, self.var_type, self.init_value)
        return line


    def check(self):
        result = text_value_check( self.result, self.min_value, self.max_value )
        return result


    def __repr__(self):
        return "Variable(name=%s, type=%s, init_value=%s, min_value=%s, max_value=%s)" % (self.name, self.var_type, self.init_value, self.min_value, self.max_value)

class PouData:
    def __init__(self, pou_name, fb_name="", var_type="", check_var_name="", init_value="", check_min="", check_max="" ):
        self.pou_name = pou_name
        self.fb_name = fb_name
        self.var_type = var_type
        self.check_var_name = check_var_name
        self.init_value = init_value
        self.check_min = check_min
        self.check_max = check_max
        self.variable_list = []
        self.other_statement_list = []
        self.log = []
        self.fb_result = 0

    def add_log(self,log_text):
        log_tool.put_log( log_text )
        self.log.append( log_text )

    def flush_log(self):
       for line in self.log:
           log_print( line )

    def add_variable(self, variable):
        self.variable_list.append(variable)

    def init_statement(self):
        statement = []
        for variable in self.variable_list:
            line = variable.init_statement()
            statement.append(line)
        if self.check_var_name != "":
            line = '%s : %s := %s;' % (self.check_var_name, self.var_type, self.init_value)
            statement.append(line)
        statement.append( "checkcount : INT := 0;")
        return '\n'.join(statement) + '\n'

    def check_statement(self):
        statement = []
        for variable in self.variable_list:
            lines = variable.check_statement()
            statement.extend(lines)
        if self.check_var_name != "":
            line = '%s : %s := %s;' % (self.check_var_name, self.var_type, self.init_value)
            statement.append(line)
        return '\n'.join(statement)

    def other_statement(self):
        return '\n'.join(self.other_statement_list)

    def fb_statement(self):
        if self.fb_name == None or self.fb_name=="":
            return "checkcount:=1;"
        param_text = ""
        for variable in self.variable_list:
            if param_text != "":
                param_text += ","
            param_text += variable.name

        statement = "%s:= %s(%s);\ncheckcount:=1;" % (self.check_var_name, self.fb_name, param_text)
        return statement

    def is_not_csv(self):
        result = len(self.other_statement_list)>0
        return result

    def collect_result(self,execution = None):
        checkcount_name = self.pou_name +".checkcount"
        checkcount = execution.read_value(checkcount_name)
        #log_print("checkcount: " + checkcount)
        checkcount = int(checkcount.split('#')[1])
        #print("chk:"+str(checkcount))
        if checkcount == 0:
            return False
        else:
            time.sleep(5)
            for variable in self.variable_list:
                pou_variable_name = self.pou_name + '.' + variable.name
                #log_print( pou_variable_name, self )
                if execution != None:
                    variable.result = execution.read_value(pou_variable_name)
                    log_print( "%s=%s" % (pou_variable_name, variable.result), self )
                else:
                    variable.result = variable.min_value
            log_print(variable.result)
            pou_variable_name = self.pou_name + '.' + self.check_var_name
            #log_print( "self.fb_name="+self.fb_name, self )
            if len(self.fb_name) <= 0:
                return True
            if __name__=="__main__":
                self.fb_result = self.check_min
                return True
            # log_print( "self.check_var_name="+pou_variable_name, self )
            self.fb_result = execution.read_value(pou_variable_name)
            log_print( "%s=%s" % (self.check_var_name,self.fb_result), self )
            return True
    
    def read_array(self,execution=None):
        pou_name = make_function_name( 'POU', self.pou_name)
        array_value = []
        for i in range(9) :
            pou_array_name = pou_name + '.' + 'checkarray' + '[' + str(i) + ']'
            before_get_item = execution.read_value(pou_array_name)
            type_text,value_text = string_to_typevalue( before_get_item )
            array_value.append(value_text)
        return array_value


    def check_array_value(self,after_reset_value,expected,befor_reset_value,pou_name,type_text):
        if after_reset_value == expected :
            log_print('{} : initial_value : {} = after_value : {} :OK'.format(pou_name,befor_reset_value,after_reset_value))
        else :
                result = text_value_check_type(type_text,after_reset_value,befor_reset_value,max_value=None)
                if result :
                    log_print('{}:initial_value : {} = after_value : {} :OK'.format(pou_name,befor_reset_value,after_reset_value))
                else:
                    log_print('{}:initial_value : {} = after_value : {} :NG'.format(pou_name,befor_reset_value,after_reset_value))

    def check_array(self, before_reset_array, execution=None) :
        checkarray_length = len(before_reset_array)

        pou_name = make_function_name( 'POU', self.pou_name)
        after_reset_array = []
        for i in range(checkarray_length) :
            pou_array_name = pou_name + '.' + 'value_'+ str(i)
            after_get_item = execution.read_value(pou_array_name)
            type_text,value_text = string_to_typevalue( after_get_item )
            if i in (0,2,3):
                
                self.check_array_value(value_text,'0',before_reset_array[i],pou_name,type_text)
            elif i in (6,7,8):
                
                self.check_array_value(value_text,"",before_reset_array[i],pou_name,type_text)
            elif i == 4:
               
                self.check_array_value(value_text,"0ms",before_reset_array[i],pou_name,type_text)
            elif i == 5:
                
                self.check_array_value(value_text,"1970-1-1",before_reset_array[i],pou_name,type_text)
            elif i == 1:
                
                self.check_array_value(value_text,"FALSE",before_reset_array[i],pou_name,type_text)


    def check_values(self):
        all_result = True
        for variable in self.variable_list:
            result = variable.check()
            all_result &= all_result
            if result:
                log_print('{}={}:OK'.format(variable.name, variable.result), self )
            else:
                log_print('{}={}:NG'.format(variable.name, variable.result), self )

        if len(self.fb_name)>0:
            result = self.fb_result == self.check_min
            #result = text_value_check(self.fb_result, self.check_min, self.check_max)
            all_result &= result
            log_print('{}={}:{}'.format(self.fb_name, self.fb_result, 'OK' if result else 'NG'), self )

        return all_result

    def check_other_statement(self,execution):
        pou_variable_name = self.pou_name + '.' + self.check_var_name
        pou_name = make_function_name( 'POU', self.pou_name)
        checkcount_name = pou_name +".checkcount"
        #log_print( "checkcount_name="+ checkcount_name)
        checkcount = execution.read_value(checkcount_name)
        #log_print( "checkcount="+ checkcount)
        separatecount = checkcount.split('#',1)[1]
        #print("value0 : "+ separatecount)
        if int(separatecount) <= 0:
            return False
        time.sleep(5)
        #log_print( "get the checkcount"+ checkcount)
        #print("value1"+ pou_name)
        pou_variable_name = pou_name+'.'+'checkcount'
        #print("value2"+pou_variable_name)
        checkcount = execution.read_value(pou_variable_name)
        #print(pou_variable_name + "="+checkcount)
        separatecount = checkcount.split('#',1)[1]
        #print("value4"+separatecount)
        typeconversioncount =int(separatecount)
        for i in range(typeconversioncount):
            pou_variable_name = pou_name+'.'+'checkarray['+str(i)+']'
            checkarray = execution.read_value(pou_variable_name)
            formatcheckarray = checkarray.replace("'","")
            log_print(formatcheckarray, self )
            log_tool.put_log( formatcheckarray)
        return True


    def other_statement(self,header):
        if len( self.other_statement_list )<0:
            return None

        statement_list = []
        is_start = False
        for i in range(len(self.other_statement_list)):
            if self.other_statement_list[i]==header:
                is_start = True
                continue
            if is_start and self.other_statement_list[i].startswith( "_" ):
                break
            if not is_start:
                continue
            statement_list.append( self.other_statement_list[i] )

        if len(statement_list) <= 0:
            return None
        return statement_list

    def __repr__(self):
        return "PouData(pou_name=%s, fb_name=%s, var_type=%s, check_var_name=%s, init_value=%s, check_min=%s, check_max=%s, variable_list=%s)" % (self.pou_name, self.fb_name, self.var_type, self.check_var_name, self.init_value, self.check_min, self.check_max, self.variable_list)

def parse_value(value):
    if ':' in value:
        min_value, max_value = value.split(':')
    else:
        min_value = max_value = value
    return min_value, max_value

def create_from_file(file_name):
    pou_name, file_extension = os.path.splitext(os.path.basename(file_name))
    try:
        with open(file_name, 'r') as file:
            other_statement_list = file.readlines()
        for i in range(len(other_statement_list)):
            other_statement_list[i] = other_statement_list[i].replace( "\n", "")
    except Exception as e:
        log_print( "error "+file_name)
        return

    pou_data = PouData( pou_name )
    pou_data.other_statement_list = other_statement_list
    return pou_data

def read_csv(file_path):
    pou_data_list = {}
    last_pou_name = ""
    with open(file_path, mode='r') as csvfile:
        for line in csvfile:
            if line.startswith('#'):
                continue
            if line.startswith('@'):
                pou_data = create_from_file( line[1:].strip() )
                pou_data_list[pou_data.pou_name] = pou_data
                continue

            row = line.split(',')

            column = 0
            pou_name = row[0]
            if len( row )<2 :
                pou_data = PouData(pou_name)
                pou_data_list[pou_data.pou_name] = pou_data
                last_pou_name = pou_name
                continue
            fb_name = row[1]

            if len(fb_name) > 1:
                check_var_name = row[2]
                var_type = row[3]
                init_value = row[4]
                check_min, check_max = parse_value(row[5])
                pou_data = PouData(pou_name, fb_name, var_type, check_var_name, init_value, check_min, check_max)
            else:
                pou_data = PouData(pou_name)
                fb_name = None

            column = 6
            while column < len(row):
                var_name = row[column]
                var_type = row[column+1]
                var_init_value = row[column+2]
                var_min_value, var_max_value = parse_value(row[column+3])
                variable = Variable(var_type, var_name, var_init_value, var_min_value, var_max_value)
                pou_data.add_variable(variable)
                column += 4
            pou_data_list[pou_data.pou_name] = pou_data
            last_pou_name = pou_data.pou_name
    return pou_data_list


if __name__ == "__main__":
    class log_tool:
        def put_log( text ):
            log_print( text )


#    file_path = r'C:\mos-system-tests\Test\TestData\StanaredFuFb\ControlApplication_DataType_Standard.csv'
    file_path = r'ControlApplication_DataType_Standard.csv'

    pou_data_list = read_csv(file_path)
    for name in pou_data_list:
        pou_data = pou_data_list[name]
        init_text = pou_data.init_statement()
        pou_data.collect_result()
        # check_text = pou_data.check_statement()
        fb_statement = pou_data.fb_statement()
        #fb_check_text = pou_data.fb_check_statement()
        other_statement = pou_data.other_statement("_FB_declaration")
        function_declaration_statment = pou_data.other_statement("_FB_declaration")
        function_implementation_statment = pou_data.other_statement("_FB_implementation")
        pou_declaration_statment = pou_data.other_statement("_pou_declaration")
        pou_implementation_statment = pou_data.other_statement("_pou_implementation")
        is_csv = pou_data.is_csv()
        pou_data.collect_result()
        pou_data.check_values()
        pou_data.flush_log()
        print(pou_data)
