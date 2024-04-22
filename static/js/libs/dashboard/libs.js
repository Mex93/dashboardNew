function Enum(obj)
{
    // итоговый объект
    const newObj = {};

    // проходимся по каждому свойству переданного в функцию объекта
    for( const prop in obj )
    {
        // проверяем наличие собственного свойства у объекта
        if (obj.hasOwnProperty(prop)) {

            // помещаем в новый объект специальный примитивный тип JavaScript Symbol
            newObj[prop] = Symbol(obj[prop]);
        }
    }

    // делаем объект неизменяемым (свойства объекта нельзя будет изменить динамически)
    return Object.freeze(newObj);
}


function findWord(str, word) {
    return str.includes(word)
}
function getrdata()
{
    return Math.floor((Math.random() * 100) + 1);
}
function getRandomInt(max)
{
    return Math.floor(Math.random() * max);
}

// export class StringParser
// {
//     static PARSE_TYPE = Enum({
//         TO_INT_ARR: 1,
//         TO_STR_ARR: 2,
//         NONE: 0
//     });
//     #current_parseType = StringParser.PARSE_TYPE.NONE;
//
//     // constructor()
//     // {
//     //     return true;
//     // }
//
//     Type(parseType = StringParser.PARSE_TYPE)
//     {
//         if(parseType === StringParser.PARSE_TYPE.TO_INT_ARR || parseType === StringParser.PARSE_TYPE.TO_STR_ARR)
//         {
//             this.#current_parseType = parseType;
//             return true;
//         }
//         else reportError("Undefined Parse Type");
//         return false;
//     }
//     Parsed(objSTR)
//     {
//         if((objSTR.length > 0) &&
//             (typeof objSTR === 'string'))
//         {
//             let cparse_type = this.#current_parseType;
//             if(cparse_type !== StringParser.PARSE_TYPE.NONE)
//             {
//                 let arr = objSTR;
//                 for(let i = 0;i<objSTR.length;i++)
//                 {
//                     arr = arr.replace("[", "");
//                     arr = arr.replace("]", "");
//                     arr = arr.replace("'", "");
//                     arr = arr.replace(" ", "");
//                     if(arr.length === 0)break;
//                 }
//                 if(arr.length > 0)
//                 {
//                     arr = arr.split(",");
//                     if(cparse_type === StringParser.PARSE_TYPE.TO_INT_ARR)
//                     {
//                         let completed_arr = Array()
//                         let count = 0;
//                         let buff = null;
//                         for (let keys in arr)
//                         {
//                             buff = parseInt(arr[keys]);
//                             if(isNaN(buff))continue;
//                             completed_arr[count] = buff;
//                             count++;
//                         }
//                         if(completed_arr.length > 0 && count > 0)
//                         {
//                             return completed_arr;
//                         }
//                     }
//                     else if(cparse_type === StringParser.PARSE_TYPE.TO_STR_ARR)
//                     {
//                         // console.log(arr);
//                         // console.log(typeof arr);
//                         if(arr.length > 0)
//                         {
//                             return arr;
//                         }
//                     }
//                 }
//             }
//         }
//         return false;
//     }
// }


// export function getNullArrIndexesInResult5Mins(
//     arr = [],
//     start_index = 0,
//     delay_count = 0,
//     number_null = 0,
//     max_size = arr.length)
// {
//     // найдёт пустые элементы массива координат и вернёт массивов с индексами нулей
//     let currentDelayCount= 0;
//     let arr_DeletedPoints = []
//     let newArrSize = 0;
//     if((max_size > 0) && (start_index < max_size))
//     {
//         for(let i = start_index; i<max_size; i++)
//         {
//             if(number_null === arr[i])
//             {
//                 if(currentDelayCount < delay_count)
//                 {
//                     currentDelayCount++;
//                     continue;
//                 }
//                 arr_DeletedPoints[newArrSize] = i;
//                 newArrSize++;
//             }
//         }
//         if(arr_DeletedPoints.length > 0)
//         {
//             return arr_DeletedPoints;
//         }
//     }
//     return false;
// }


const MAX_LINES = 4;
const MAX_LINES_CHART_ID = [-1,-1,-1,-1];
const LINE_ID = {
    NONE: 0,
    FIRST: 1,
    DOUBLE: 2,
    THIRD: 3,
    FOUR: 4
};

const PARAMS_ID = Enum({
    LINE_NONE: 0,
    LINE_DAY_PLANE: 1,
    LINE_HOUR_PLANE: 2,
    LINE_FIVE_MINS: 3,
    LINE_FIVE_MINS_DOTS_ARR: 4,
    LINE_FIVE_MINS_MAIN_ARR: 5,
    LINE_HOURS: 6,
    LINE_HOURS_DOTS_ARR: 7,
    LINE_HOURS_MAIN_ARR: 8,
    LINE_NAME: 9,
    LINE_ID: 10,
    LINE_CANVAS_ID: 11,
    LINE_DATE_STATUS: 12
});
class LineParams
{
    #lineID;
    #lineName= String();
    #lineInHour = new Map();
    #lineInFiveMins = new Map();
    #lineDayPlane;
    #chartCanvasID;
    #lineHourPlane;
    #successCreatedStatus = false;
    #dateStatus = false;

    constructor(lineName, chartCanvasID, lineID)
    {
        if(lineName.length > 2)
        {
            if(lineID >= 0 && lineID <= 4)
            {
                this.#SetDefaultParams();
                this.#successCreatedStatus = true;
                this.#lineID = lineID;
                this.#lineName = lineName;
                this.#chartCanvasID = chartCanvasID;
            }
        }
    }
    SetParams(paramType, paramsToSet)
    {
        switch(paramType)
        {
            case PARAMS_ID.LINE_DATE_STATUS:
            {
                this.#dateStatus = paramsToSet;
                return true;
            }
            case PARAMS_ID.LINE_NAME:
            {
                this.#lineName = paramsToSet;
                return true;
            }
            case PARAMS_ID.LINE_DAY_PLANE:
            {
                this.#lineDayPlane = paramsToSet;
                return true;
            }
            case PARAMS_ID.LINE_HOUR_PLANE:
            {
                this.#lineHourPlane = paramsToSet;
                return true;
            }
            case PARAMS_ID.LINE_FIVE_MINS:
            {
                this.#lineInFiveMins = new Map(Object.entries(paramsToSet));
                return true;
            }
            case PARAMS_ID.LINE_HOURS:
            {
                this.#lineInHour = new Map(Object.entries(paramsToSet));
                return true;
            }
        }
        return false;
    }
    GetParams(paramType)
    {
        if(this.#successCreatedStatus === true)
        {
            switch(paramType)
            {
                case PARAMS_ID.LINE_ID:
                {
                    return (this.#lineID);  // вернёт с +1, не с нуля
                }
                case PARAMS_ID.LINE_DATE_STATUS:
                {
                    return (this.#dateStatus);
                }
                case PARAMS_ID.LINE_NAME:
                {
                    return (this.#lineName);
                }
                case PARAMS_ID.LINE_DAY_PLANE:
                {
                    return (this.#lineDayPlane);
                }
                case PARAMS_ID.LINE_HOUR_PLANE:
                {
                    return (this.#lineHourPlane);
                }
                case PARAMS_ID.LINE_FIVE_MINS_DOTS_ARR:
                {
                    return Array.from(this.#lineInFiveMins.values());
                }
                case PARAMS_ID.LINE_FIVE_MINS_MAIN_ARR:
                {
                    return Array.from(this.#lineInFiveMins.keys());
                }
                case PARAMS_ID.LINE_FIVE_MINS:
                {
                    return structuredClone(this.#lineInFiveMins);
                }
                case PARAMS_ID.LINE_HOURS_DOTS_ARR:
                {
                    return Array.from(this.#lineInHour.values());
                }
                case PARAMS_ID.LINE_HOURS_MAIN_ARR:
                {
                    return Array.from(this.#lineInHour.keys());
                }
                case PARAMS_ID.LINE_HOURS:
                {
                    return structuredClone(this.#lineInHour);
                }
                case PARAMS_ID.LINE_CANVAS_ID:
                {
                    return this.#chartCanvasID;
                }
            }
        }

        return false;
    }
    #SetDefaultParams()
    {
        this.#lineID = LINE_ID.NONE;
        this.#lineName = "None";
        this.#lineInHour.clear();
        this.#lineInFiveMins.clear();
        this.#lineDayPlane = 0;
        this.#lineHourPlane = 0;
        this.#successCreatedStatus = false;
    }
    static GetObjectIDFromLineID(objectArr, lineID)
    {
        if(typeof objectArr === 'object')
        {
            for(let i = 0; i < objectArr.length; i++)
            {
                if(objectArr[i].#successCreatedStatus === true)
                {
                    if(lineID === objectArr[i].#lineID)
                    {
                        return objectArr[i];
                    }
                }
            }
        }
        return -1;
    }
}
const INCOMMING_ARR_TYPE = {
    HOURS: 0,
    FIVEMINS: 1,
    DAY_PLANE: 2,
    HOUR_PLANE: 3,
    LINEID: 4

};


const JOB_DAY_TYPE = Enum({
    TYPE_DAY: 1,
    TYPE_NIGHT: 2,
    TYPE_NONE: 0});

function GetJobTypeArr(arr_night, arr_day, current_arr)
{
    let arr = Array.from(current_arr.keys());  // получим ключи в массив
    //console.log(arr);
    for(let i = 0; i < arr.length; i++)
    {
        if(arr_night.indexOf(arr[i]) !== -1)
        {
            return arr_night;
        }
        else if(arr_day.indexOf(arr[i]) !== -1)
        {
            return arr_day;
        }
    }
    return JOB_DAY_TYPE.TYPE_NONE;
}


function GetStandartFMinsAssocArr(current_arr, end_lenght)
{
    const mins_array = [];
    for(let i = 0; i < 12; i++)
    {
        mins_array[i] = `${5 * i}`.padStart(2, '0')
    }
    const list_hour_night = ["20", "21", "22", "23", "00", "01", "02", "03", "04", "05", "06", "07"];
    const list_hour_day = ["08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"]
    let currentJobHoursArr = GetJobTypeArr(list_hour_night, list_hour_day, current_arr);
    if(currentJobHoursArr !== JOB_DAY_TYPE.TYPE_NONE)
    {
        let buff_arr = new Map();
        let current_lenght = 0;
        for(let i_hour = 0; i_hour < 12; i_hour++)
        {
            for(let i_mins = 0; i_mins < 12; i_mins++)
            {
                buff_arr.set(`${currentJobHoursArr[i_hour]}:${mins_array[i_mins]}`, 0);
                if(current_lenght > end_lenght)
                {
                    current_lenght = true;
                    break;
                }
                current_lenght++;
            }
            if(current_lenght === true)
            {
                //console.log(current_lenght);
                break;
            }
        }
        if(buff_arr.size > 0)
        {
            return buff_arr;
        }
        //console.log(buff_arr);
    }
    return false;
}

function getIntervalArr(old_index, inFindArr, findStr)
{
    old_index = (old_index === -1) ? 0: old_index;
    for(let i= old_index; i < inFindArr.length; i++)
    {
        if(inFindArr[i].indexOf(findStr) !== -1)
        {
            return i;
        }
    }
    return -1;
}


function getStandartPHMainLandArr()
{
    return [
        '08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
        '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00',
        '18:00-19:00', '19:00-20:00'];
}
function getStandartPHMainLandArrEx()
{
    return [
        '08', '09', '10', '11', '12',
        '13', '14', '15', '16', '17',
        '18', '19'];
}

function getRandom5minsDots()
{
    let def_dots_line = [];
    for(let i = 0; i < 12*12; i++)
    {
        def_dots_line[i] = getrdata();
    }
    return def_dots_line;
}
function getRandomPHDots()
{
    let def_dots_line = [];
    for(let i = 0; i < 12; i++)
    {
        def_dots_line[i] = getrdata();
    }
    return def_dots_line;
}
function getStandart5minsMainLandArr()
{
    // В часу 12 раз по 5
    // В смене 12 часов
    // общее количество повторений за смену= 12 * 12 == 144

    let now = new Date();
    let fixed_date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 8, 0,
        0);
    let start_unix_time = Math.floor(fixed_date.getTime() / 1000);

    //console.log(start_unix_time)
    let arr = [];
    let buff_min_str = "";
    let buff_hour_str = "";
    let buff_str = ""
    // формируем строку со временем 5 min
    for(let i = 0; i < 12*12; i++)
    {
        let currentd = new Date((start_unix_time + ((5*60) * i)) * 1000);
        buff_hour_str = String(currentd.getHours()).padStart(2, '0')
        buff_min_str = String(currentd.getMinutes()).padStart(2, '0') // сформируем строку и добавим нули спереди
        buff_min_str = buff_min_str.padStart(-2, '0') // добавим нолики сзади
        buff_str = buff_hour_str + ":" + buff_min_str;
        arr[i] = buff_str;
        // сonsole.log(buff_str)
    }
    return arr
}


export {
    getStandart5minsMainLandArr,
    getRandomPHDots,
    getRandom5minsDots,
    getStandartPHMainLandArrEx,
    getStandartPHMainLandArr,
    getRandomInt,
    getrdata,
    findWord,
    Enum,

    MAX_LINES,
    MAX_LINES_CHART_ID,
    LINE_ID,
    PARAMS_ID,
    LineParams,
    INCOMMING_ARR_TYPE,
    GetStandartFMinsAssocArr,
    getIntervalArr,
}

