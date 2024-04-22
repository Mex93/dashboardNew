import {
    Enum
} from './utils.js';
class StringParser
{
    static PARSE_TYPE = Enum({
        TO_INT_ARR: 1,
        TO_STR_ARR: 2,
        NONE: 0
    });
    #current_parseType = StringParser.PARSE_TYPE.NONE;

    // constructor()
    // {
    //     return true;
    // }

    Type(parseType = StringParser.PARSE_TYPE)
    {
        if(parseType === StringParser.PARSE_TYPE.TO_INT_ARR || parseType === StringParser.PARSE_TYPE.TO_STR_ARR)
        {
            this.#current_parseType = parseType;
            return true;
        }
        else reportError("Undefined Parse Type");
        return false;
    }
    Parsed(objSTR)
    {
        if((objSTR.length > 0) &&
            (typeof objSTR === 'string'))
        {
            let cparse_type = this.#current_parseType;
            if(cparse_type !== StringParser.PARSE_TYPE.NONE)
            {
                let arr = objSTR;
                for(let i = 0;i<objSTR.length;i++)
                {
                    arr = arr.replace("[", "");
                    arr = arr.replace("]", "");
                    arr = arr.replace("'", "");
                    arr = arr.replace(" ", "");
                    if(arr.length === 0)break;
                }
                if(arr.length > 0)
                {
                    arr = arr.split(",");
                    if(cparse_type === StringParser.PARSE_TYPE.TO_INT_ARR)
                    {
                        let completed_arr = Array()
                        let count = 0;
                        let buff = null;
                        for (let keys in arr)
                        {
                            buff = parseInt(arr[keys]);
                            if(isNaN(buff))continue;
                            completed_arr[count] = buff;
                            count++;
                        }
                        if(completed_arr.length > 0 && count > 0)
                        {
                            return completed_arr;
                        }
                    }
                    else if(cparse_type === StringParser.PARSE_TYPE.TO_STR_ARR)
                    {
                        // console.log(arr);
                        // console.log(typeof arr);
                        if(arr.length > 0)
                        {
                            return arr;
                        }
                    }
                }
            }
        }
        return false;
    }
}


export {
    StringParser,
}

