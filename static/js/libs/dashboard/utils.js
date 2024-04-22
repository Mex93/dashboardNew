import {
    JOB_DAY_TYPE
} from './common.js';


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


const findWord = (str, word) => str.includes(word);
const getrdata = () => Math.floor((Math.random() * 100) + 1);
const getRandomInt = (max) => Math.floor(Math.random() * max);

function GetAnyResultIn(findParam, arr)
{
    let resultCounts = 0;
    if(Array.isArray(arr))
    {
        arr.forEach((el) =>
        {
            if(el === findParam)
            {
                resultCounts++;
            }
        })
    }
    return resultCounts;
}


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

const getStandartPHMainLandArr = () => [
    '08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
    '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00',
    '18:00-19:00', '19:00-20:00'];

const getStandartPHMainLandArrEx = () => [
    '08', '09', '10', '11', '12',
    '13', '14', '15', '16', '17',
    '18', '19'];


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

function SetMakeScoreString({dayPlane = 0,
                                dayFact = 0,
                                factSpeed = 0,
                                dayForecast= 0,
                                tvCSSAveragePHForPlan,
                                tvCSSForecastOnDay,
                                defColor
                                })
{
    if (Number.isInteger(dayFact) &&
        Number.isInteger(factSpeed) &&
        Number.isInteger(dayPlane) &&
        Number.isInteger(dayForecast))
    {
        // Отключено. Не исполняются HTML теги
        // return (`План: ${dayPlane} шт
        // Факт: ${dayFact} шт
        // Скорость: ${tvCSSAveragePHForPlan}${factOnHour} ${defColor}шт/час
        // Прогноз за день: ${tvCSSForecastOnDay}${dayForecast} ${defColor}шт`);

        return (`План: ${dayPlane} шт     
        Факт: ${dayFact} шт     
        Скорость: ${factSpeed} шт/час     
        Прогноз за день: ${dayForecast} шт`);

    }
    return 'Empty field due error';
}

function ConvertCssColorForRGB(cssColor)
{
    if(String(cssColor))
    {
        switch(cssColor)
        {
            case "_XS":return '#e51937';
            case "_S":return '#fd7e14';
            case "_M":return '#ffc107';
            case "_L":return '#28a745';
            case "_XL":return '#1bbbff';
        }
    }
    return '#C0C0C0';  // _NI
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

    ConvertCssColorForRGB,
    SetMakeScoreString,
    GetStandartFMinsAssocArr,
    getIntervalArr,
}

