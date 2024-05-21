import {
    LINE_ID,

} from './libs/dashboard/common.js';

import {
    getStandart5minsMainLandArr,
    getRandomPHDots,
    getRandom5minsDots,
    getStandartPHMainLandArrEx,
    getStandartPHMainLandArr,
    getRandomInt,
    GetStandartFMinsAssocArr,
    getIntervalArr,
    SetMakeScoreString,
    ConvertCssColorForRGB,

} from './libs/dashboard/utils.js';

import {
    LineParams,
    PARAMS_ID,
    INCOMMING_ARR_TYPE,
    MAX_VRN_LINES,
    MAX_ALL_LINES,
    CUpdatedLines,
    CChartID,
    CDebugger,
    CLineShowType,
    CHTMLBlocks

} from './libs/dashboard/Classes.js';


let debug = false;
const cUpdatedInfoUnit = new CUpdatedLines();
const cChartIDUnit = new CChartID();
const cDebug = new CDebugger(true);
const cHTMLUnit = new CHTMLBlocks();
const cHTMLType = new CLineShowType();

const DEFAULT_LINE_DAY_PLANE = 777;
let updateTimerCounts = 0;
let onCreateUpdateTimerID = -1;
let onUpdateTimerID = -1;
const MAX_UPDATE_FOR_CREATE_GRAF = 60;  // sec
let firstLoadStatus = true;



function FirstLoadAfterDelay()
{
    CreateChartHandlersData();

    let timerID = undefined;
    setTimeout(() => // второй раз для обновления
    {
        CreateChartHandlersData();

       timerID = setInterval(UpdateFunc,12000); // обновлялка, можно менять
       onUpdateTimerID = timerID;
       onCreateUpdateTimerID = setInterval(OnCreateGraphUpdate, 2000) // не рекомендуется менять

    },1000);

    let UpdateFunc = () =>{
        CreateChartHandlersData();
    }
    // Kill this timer ()_()
    setTimeout(() =>
    {
        clearInterval(timerID);
        location.reload();
    }, 1_800_000)  // через пол часа автоматический перезапуск на всякий случай
}

// Таймер обновления для создания.
// Умирает после удачного создания.
// 6 секунд нет результата - перезагрузит страницу

function OnCreateGraphUpdate()
{
    let len = cChartIDUnit.GetLenght();
    if(len > 0)
    {
        if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.KZ))
        {
            if(len <= 1)
            {
                document.getElementById(cHTMLUnit.GetOnBlocksName(0)).style.display = 'block';

                // удаление пустых холстов
                document.getElementById('getdate_dialog').style.display = 'none';
            }
            else Error("(OnCreateGraphUpdate) => Count of Grafics > 1!");
        }
        else if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.VRN))
        {
            if(len <= MAX_VRN_LINES)
            {
                let currentNode = null;
                let currentCanvasID = null;
                let delSection = null;
                for(let i = 0; i < len; i++)
                {
                    currentNode = document.querySelector(`#${cHTMLUnit.GraphDivPlaceSpanID(len-1, i)}`);
                    currentCanvasID = document.getElementById(cHTMLUnit.GetGraphCSSName(i));
                    currentNode.parentNode.append(currentCanvasID);

                    document.getElementById(cHTMLUnit.GetGraphCSSName(i)).style.display = 'block';
                }
                // удаление пустых блоков
                let savedBlock = cHTMLUnit.GetOnBlocksName(len-1);
                document.getElementById(savedBlock).style.display = 'block';
                for(let i = 0; i < cHTMLUnit.GetOnBlocksLen(len-1); i++)
                {
                    delSection = document.getElementById (`${cHTMLUnit.GetOnBlocksName(i)}`);
                    if(delSection !== null)
                    {
                        if(delSection.id === savedBlock)
                        {
                            continue;
                        }
                        delSection.remove();
                    }
                }
                // удаление пустых холстов
                for(let i = len; i < cHTMLUnit.GetGraphCSSLen(); i++)
                {
                    delSection = document.getElementById (`${cHTMLUnit.GetGraphCSSName(i)}`);
                    if(delSection !== null)
                    {
                        //cDebug.dprint(delSection);
                        delSection.remove();
                    }
                }

                document.getElementById('getdate_dialog').style.display = 'none';
            }
            else Error("(OnCreateGraphUpdate) => Count of Grafics > 4!");
        }
        else if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.ALL))
        {
            if(len <= MAX_ALL_LINES)
            {
                let iindex = null;
                for(let i = 0; i < len; i++)
                {
                    iindex = document.getElementById(cHTMLUnit.GetGraphCSSName(i));
                    if(iindex !== null)
                    {
                        iindex.style.display = 'block';
                    }
                }
                // удаляем пустые
                for(let i = len; i < cHTMLUnit.GetGraphCSSLen(i); i++)
                {
                    iindex = document.getElementById(cHTMLUnit.GetGraphCSSName(i));
                    if(iindex !== null)
                    {
                        iindex.remove();
                    }
                }
                let savedBlock = cHTMLUnit.GetOnBlocksName(cHTMLUnit.GetOnBlocksLen()-1);
                document.getElementById(savedBlock).style.display = 'block';


                document.getElementById('getdate_dialog').style.display = 'none';
            }
            else Error("(OnCreateGraphUpdate) => Count of Grafics > 4!");
        }
        else Error("(OnCreateGraphUpdate) => Error Graf HTML ShowType!");


        cDebug.dprint("Отработал обновление показа css для  " + len);

        clearInterval(onCreateUpdateTimerID);
        onCreateUpdateTimerID = -1;
        setInterval(OnGraphUpdate, 2000);

        firstLoadStatus = false;
    }
    else
    {
        if(updateTimerCounts === 0)
        {
            document.getElementById('getdate_dialog').style.display = 'none';
            document.getElementById('reload_dialog').style.display = 'block';
            clearInterval(onUpdateTimerID);
        }
        updateTimerCounts++;
        if(updateTimerCounts > MAX_UPDATE_FOR_CREATE_GRAF)
        {
            //Error("(OnCreateGraphUpdate) => Page has ben reloaded! Error for 0 count graf");
            cDebug.dprint("(OnCreateGraphUpdate) => Page has ben reloaded! Error for 0 count graf");
            updateTimerCounts = 0;
            location.reload();
        }
    }
}

// Update Timer запускается после отработки таймера обновления
// Перезагрузит страницу, если графиков станет больше
function OnGraphUpdate()
{
    if(!firstLoadStatus) // если запуск не первичный
    {
        let len = cChartIDUnit.GetLenght();
        if(len > 0)
        {
            let countOfLines = cUpdatedInfoUnit.GetCountLines();
            //console.log(countOfLines, len);
            if(countOfLines !== len) // количество линий не совпадает со значением первой загрузки
            {
                cDebug.dprint("(OnCreateGraphUpdate) => Page has ben reloaded! Error for new graf");
                //location.reload();
            }
        }
    }
}


function CreateChartHandlersData()
{
    cDebug.dprint("query ->");
    // блок обработчик

    let CLine_1 = new LineParams("Первая линия",cHTMLUnit.GetCanvasArr(0), LINE_ID.FIRST);
    let CLine_2 = new LineParams("Вторая линия",cHTMLUnit.GetCanvasArr(1), LINE_ID.DOUBLE);
    let CLine_3 = new LineParams("Третья линия",cHTMLUnit.GetCanvasArr(2), LINE_ID.THIRD);
    let CLine_4 = new LineParams("Четвёртая линия",cHTMLUnit.GetCanvasArr(3), LINE_ID.FOUR);
    let CLine_5 = new LineParams("Линия Казахстан",cHTMLUnit.GetCanvasArr(4), LINE_ID.FIVE);

    let CLines_obj = [CLine_1, CLine_2, CLine_3, CLine_4, CLine_5];
    // получим инфу и обработаем, положим в массивы

    let max_lines= cHTMLType.getMaxLines();
    if(debug)
    {
        cUpdatedInfoUnit.ClearStats();
        let def_down_hour_time = getStandartPHMainLandArrEx();
        let def_down_line_5m = getStandart5minsMainLandArr();
        for(let i= 0; i < max_lines; i++) // MAX_LINES
        {
            let findObjectID = -1;
            if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.KZ))
            {
                findObjectID = LineParams.GetObjectIDFromLineID(
                    CLines_obj,
                    LINE_ID.FIVE);
            }
            else if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.VRN))
            {
                findObjectID = LineParams.GetObjectIDFromLineID(
                    CLines_obj,
                    i+1);
            }
            else if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.ALL))
            {
                findObjectID = LineParams.GetObjectIDFromLineID(
                    CLines_obj,
                    i+1);
            }
            if(findObjectID !== -1)
            {
                let arr_ph_dots = getRandomPHDots();
                let arr_5mins_dots = getRandom5minsDots();
                //
                let dayPlane = getRandomInt(900+200);
                findObjectID.SetParams(PARAMS_ID.LINE_DAY_PLANE,
                    dayPlane);

                findObjectID.SetParams(PARAMS_ID.LINE_DAY_FACT,
                    getRandomInt(900+200));

                findObjectID.SetParams(PARAMS_ID.LINE_HOUR_FACT_SPEED,
                    getRandomInt(dayPlane / 10.3));  // Несовсем верное вычисление, просто тест

                findObjectID.SetParams(PARAMS_ID.LINE_DAY_FORECAST,
                    getRandomInt(900+200));

                findObjectID.SetParams(PARAMS_ID.LINE_CSS_SCOREBOARD,
                    getRandomInt(0));

                //
                findObjectID.SetParams(PARAMS_ID.LINE_HOUR_PLANE,
                    Number(dayPlane / 10.3));

                let buffObj = {};
                //
                def_down_line_5m.forEach((el, index) =>
                {
                    buffObj[`${el}`] = arr_5mins_dots[index];
                })

                findObjectID.SetParams(PARAMS_ID.LINE_FIVE_MINS,
                    buffObj);
                //
                buffObj = {}
                def_down_hour_time.forEach((el, index) =>
                {
                    buffObj[`${el}`] = arr_ph_dots[index];
                })

                //cDebug.dprint(buffarr);
                findObjectID.SetParams(PARAMS_ID.LINE_HOURS,
                    buffObj);
                buffObj = {}
                //
                //cDebug.dprint(findObjectID.GetParams(PARAMS_ID.LINE_FIVE_MINS));
                StoredData(findObjectID);
            }
        }
    }
    else
    {
        let html_type= CLineShowType.currentShowType;
        let encodeType = CLineShowType.convertType(html_type);
        if(encodeType === null)
        {
            Error("Error encodeType HTMLType!");
            return 1;
        }
        //console.log(encodeType)
        let json_text = '{"chtml_type": "'+ encodeType +'"}';
        let completed_json = jQuery.parseJSON(json_text);
        $.getJSON('/engine_scripts/py/launch_scripts/dashboard_get_stats.py',
            completed_json, function (data)
        {
            cUpdatedInfoUnit.ClearStats();
            // const incommingArray = JSON.parse(data)

           //cDebug.dprint(data)
            if(Array.isArray(data))
            {
                for(let i= 0; i < data.length; i++)
                {
                    let data_arr = data[i][0]
                    if(Array.isArray(data_arr))
                    {
                        console.log(data_arr);
                        let lineID = data_arr[INCOMMING_ARR_TYPE.LINEID];
                        let findObjectID = LineParams.GetObjectIDFromLineID(CLines_obj,lineID);

                        if(findObjectID !== -1)
                        {
                            if(data_arr[INCOMMING_ARR_TYPE.DAY_PLANE] === DEFAULT_LINE_DAY_PLANE)
                            {
                                continue;
                            }
                            findObjectID.SetParams(PARAMS_ID.LINE_DAY_PLANE,
                                data_arr[INCOMMING_ARR_TYPE.DAY_PLANE]);

                            findObjectID.SetParams(PARAMS_ID.LINE_HOUR_PLANE,
                                data_arr[INCOMMING_ARR_TYPE.HOUR_PLANE]);

                            findObjectID.SetParams(PARAMS_ID.LINE_FIVE_MINS,
                                data_arr[INCOMMING_ARR_TYPE.FIVEMINS]);

                            findObjectID.SetParams(PARAMS_ID.LINE_HOURS,
                                data_arr[INCOMMING_ARR_TYPE.HOURS]);
                            //cDebug.dprint(findObjectID.GetParams(PARAMS_ID.LINE_CANVAS_ID));
                            StoredData(findObjectID);
                    }
                    }
                }
            }
        }
        );
    }
}



function StoredData(unit_line)
{
    // блок данные

    //  TODO линейный график

    let standart_ph_interval_label = getStandartPHMainLandArr();
    //let standart_ph_label = getStandartPHMainLandArrEx();

    let buffName= unit_line.GetParams(PARAMS_ID.LINE_NAME);

    let fiveMinsAssocArr = unit_line.GetParams(PARAMS_ID.LINE_FIVE_MINS);
    let hoursAssocArr = unit_line.GetParams(PARAMS_ID.LINE_HOURS);
    let hoursDotsArrEx = Array.from(hoursAssocArr.values());

    // null points
    let pointsFiveMinsArr = Array.from(fiveMinsAssocArr.values());

    // подсчёт количества не пустых точек в пятиминутном лейбле данных
    let countOfFiveMinsDots = 0;
    pointsFiveMinsArr.forEach((el) =>
    {
        if(el !== 0)
            countOfFiveMinsDots++;
    })
    // подсчёт количества не пустых точек в часовом лейбле данных
    let countOfHoursDots = 0;
    hoursDotsArrEx.forEach((el) =>
    {
        if(el !== 0)
            countOfHoursDots++;
    })
    let label_keys = [];
    let barSize = 2;
    let hoursDotsArr = [];
    let hourPlane = unit_line.GetParams(PARAMS_ID.LINE_HOUR_PLANE);
    //cDebug.dprint(countOfFiveMinsDots, countOfHoursDots);
    if(countOfFiveMinsDots > 0 || countOfHoursDots > 0)
    {
        unit_line.SetParams(PARAMS_ID.LINE_DATE_STATUS,
            true);

        //cDebug.dprint(pointsFiveMinsArr);
        // TODO Формируем массив для часов
        // 1) Создаём пустой массив как пятиминутный с ключами минутами
        // 2) Буфим в него значения из массива с часами
        // 3) Для сдвига столбцов добавляем седьмой час к временной метке и добавляем в массив

        // Пустая коллекция
        let standart_mins_assoc_array =  new Map(); //
        // Сдвиг для столбцов от 7:30 (не актуально так как сдвинул позже столбы на 30 минут)
        // for(let i = 0; i < 6; i++)
        // {
        //     standart_mins_assoc_array.set(`07:` + `${30 + 5 * i}`.padStart(2, '0'), 0);
        // }
        // получаем пустую коллекцию пятиминутных меток
        let emptyAssArrWithFiveMins = GetStandartFMinsAssocArr(hoursAssocArr, fiveMinsAssocArr.size);

        // добавляем в пустую коллецию
        for (let [key, value] of emptyAssArrWithFiveMins)
        {
            standart_mins_assoc_array.set(key, value);
        }
        if(standart_mins_assoc_array === false)
        {
            // ошибка
            reportError("Error in 'job_type -> GetStandartFMinsAssocArr'");
            return false;
        }
        for (let [key, value] of hoursAssocArr)
        {
            standart_mins_assoc_array.set(key + ":30", value);
        }

        // Дописываем интервалы в лэйбл времени
        // TODO добавление временного интервала к часам (было 8:00 => 8:00 - 9:00)
        label_keys = Array.from(standart_mins_assoc_array.keys());
        //let label_items = Array.from(standart_mins_assoc_array.values());

        //console.time('FirstWay');
        label_keys.forEach((el, index) => {
            let buff_arr = el.split(':');
            let findStr = `${buff_arr[0]}:00`;
            if(el === findStr)
            {
                let old_index = -1;
                let findindex = getIntervalArr(old_index, standart_ph_interval_label, findStr + '-');
                if(findindex !== -1)
                {
                    for(let index_finded= index; index_finded < label_keys.length; index_finded++)
                    {
                        if(label_keys[index_finded] === `${buff_arr[0]}:30`)
                        {
                            label_keys[index_finded] = standart_ph_interval_label[findindex];
                            old_index = findindex;
                            break;
                        }
                    }
                }
            }
        })

        //console.timeEnd('FirstWay');
        //cDebug.dprint(label_keys);

        //cDebug.dprint(label_keys);

        // Ширина столба для баровых графиков
        barSize = 12;

        hoursDotsArr = Array.from(standart_mins_assoc_array.values())
        //let sizeOfArr = hoursDotsArr.length;
       // cDebug.dprint("Количество точек" + countOfHoursDots);
        // barSize = 12;
        // cDebug.dprint("Количество barSize" + barSize);
        //
        // if(sizeOfArr >= 0 && sizeOfArr <= 30)barSize = 1.5;
        // else  if(sizeOfArr >= 31 && sizeOfArr <= 60)barSize = 3;
        // else  if(sizeOfArr >= 61 && sizeOfArr <= 90)barSize = 4.5;
        // else  if(sizeOfArr >= 91 && sizeOfArr <= 120)barSize = 5.2;
        // else barSize = 6.5;
        // barSize = barSize*2;

        hourPlane = unit_line.GetParams(PARAMS_ID.LINE_HOUR_PLANE);

        // let chartBoxColors= [];
        // chartBoxColors.push('rgb(126, 140, 249)');
        // TODO цвет для динамических столбцов в зависимости от плана.
        //  Отключен из за того что мистеру босу не понравилось!
        // // let chartBoxDotsArr= unit_line.GetParams(PARAMS_ID.LINE_HOURS_DOTS_ARR);
        //
        // hoursDotsArr.forEach((el) => {
        //     if(el === 0)chartBoxColors.push(' ');
        //     else if(el >= hourPlane) chartBoxColors.push('rgb(53,175,52)');
        //     else if(el >= hourPlane/2 && el <= hourPlane)chartBoxColors.push('rgb(200,208,33)');
        //     else if(el >= hourPlane/3 && el <= hourPlane/2)chartBoxColors.push('rgb(231,36,36)');
        //     else chartBoxColors.push('rgb(220,2,2)');
        // })


        //cDebug.dprint(chartBoxColors);
    }
    else
    {

        return false;
        // label_keys = getStandart5minsMainLandArr();
        // hoursDotsArr = [];
        // hourPlane = 1200;  //default
        //
        // unit_line.SetParams(PARAMS_ID.LINE_DATE_STATUS,
        //     false);
    }

    let datasets_chart_5mins = {
        type: 'line',
        label: "Скорость штук/час",

        borderColor: 'rgb(0,121,255)',
        borderWidth: 4,
        borderSkipped: false,
        backgroundColor: 'rgb(57,145,239)',
        cubicInterpolationMode: 'monotone',  // сглаживание углов
        elements: {
            point:{
                borderWidth: 0,
                radius: 0,
            }
        },
        datalabels: {
            labels: {
                title: null
            }
        },
    }

    let lineID= unit_line.GetParams(PARAMS_ID.LINE_ID) -1;
    if(countOfFiveMinsDots)
    {
        datasets_chart_5mins.data = pointsFiveMinsArr;
    }
    else //
    {
        datasets_chart_5mins.data = [0];
    }
    let datasets_chart_ph = {
        type: 'bar',
        label: "Производительность штук/час",
        borderColor: 'rgba(14,67,190,0.2)',
        borderWidth: 2,
        borderRadius: 5,
        borderSkipped: false,
        backgroundColor: 'rgb(126, 140, 249)',


        cubicInterpolationMode: 'monotone',  // сглаживание углов
        barPercentage: barSize,
        categoryPercentage: 1,

        datalabels: {
            clip: true,
            align: 'start', // Выравнивание меток
            anchor: 'start', // Якорь меток
            color: 'rgb(255,255,255)', // Цвет меток
            font: {
                weight: 'bold', // Жирный шрифт меток
                size: 20,
            },
            formatter: function(value) {
                return value; // Возвращаем значение в числовом виде
            },
            title: {
                font: {
                    weight: 'bold'
                }
            }
        }
    }
    if(countOfHoursDots)
    {
        datasets_chart_ph.data = hoursDotsArr;
    }
    else
    {
        datasets_chart_ph.data = [0];
    }
    //cDebug.dprint(labelTimePoints[0]);

    let chartID = cChartIDUnit.GetChartID(lineID);
    let subtitleColor = '#c2bfbf';
    if(chartID === false)
    {

        let currentLen = cChartIDUnit.GetLenght();
        //cDebug.dprint(currentLen);
        let chartIDlocal = new Chart( // инициализируем плагин
            document.getElementById(`${cHTMLUnit.GetCanvasArr(currentLen)}`),

            {
                type: 'line',
                data: {
                    labels: label_keys, // метки по оси X
                    datasets: [
                        datasets_chart_5mins,
                        datasets_chart_ph,
                    ]
                },
                options: {

                    responsive: true,
                    maintainAspectRatio: false, //
                    scales: {
                        y: {
                            ticks: { color: '#ffffff', beginAtZero: true },
                            beginAtZero:true
                        },
                        x: {
                            ticks: { color: '#ffffff', beginAtZero: true },
                        }
                    },
                    plugins: {
                        // colors: {
                        //     forceOverride: true
                        // },

                        annotation: {
                            annotations: {
                                label: {
                                    type: 'line',
                                    display: true,
                                    yMin: hourPlane,
                                    yMax: hourPlane,
                                    position: 'start',
                                    x: 0, // смещение метки по горизонтали влево
                                    y: 0, // смещение метки по вертикали (0 - по центру)
                                    borderColor: 'rgb(136,135,135,0.93)',
                                    backgroundColor: 'rgba(250,63,63,0.62)',
                                    borderWidth: 2,
                                    //content: 'Плановая скорость шт/час',
                                    font: {
                                        size: 15,
                                    },
                                },
                            }
                        },
                        legend: {  // Настройка легенды датасетов
                            display: false,  // отключает легенду вообще к херам
                            position: 'top',  // позиция легенды
                            // регулирование дата сетс лейблов
                            labels: {
                                color: '#ffffff',
                                font: {
                                    size: 17,
                                },
                            }
                        },
                        subtitle: {
                            display: true,
                            color: subtitleColor,
                            text: 'Based Scoreboard Update in process...',
                            font: {
                                size: 20,
                                family: 'tahoma',
                                weight: 'normal',
                                style: 'italic'
                            },
                        },
                        title: {
                            display: true,
                            align: 'top',
                            color: 'rgb(189,186,186)',
                            text: `${buffName}`,
                            font: {
                                size: 20
                            },
                        },
                    },
                },
                plugins: [ChartDataLabels],
                //plugins: [ChartDataLabels]

            }
        );

        cChartIDUnit.CreatedChart(lineID, chartIDlocal);

        cDebug.dprint("Создан график LineID " + lineID);

        return lineID;
    }
    else // обновление
    {
        chartID.data.datasets = [
            datasets_chart_5mins,
            datasets_chart_ph
        ]
        chartID.data.labels = label_keys;
        chartID.options.plugins.annotation.annotations.label.yMin = hourPlane;
        chartID.options.plugins.annotation.annotations.label.yMax = hourPlane;

        let dayFact = unit_line.GetParams(PARAMS_ID.LINE_DAY_FACT);
        let factSpeed = unit_line.GetParams(PARAMS_ID.LINE_HOUR_FACT_SPEED);
        let dayForecast = unit_line.GetParams(PARAMS_ID.LINE_DAY_FORECAST);

        // деструктурируем css object
        // свойство "-" по умолчанию, если его нет у объекта
        // let cssScoreboard = unit_line.GetParams(PARAMS_ID.LINE_CSS_SCOREBOARD);
        // let {count_tv_on_5min_css: tvCSSOn5Min = "-",
        //     count_tv_average_ph_for_plan_css: tvCSSAveragePHForPlan= "-",
        //     average_fact_on_hour_css: tvCSSAverageFactOnHour= "-",
        //     count_tv_forecast_on_day_css: tvCSSForecastOnDay= "-"} = cssScoreboard
        //
        // tvCSSOn5Min = ConvertCssColorForRGB(tvCSSOn5Min);
        // tvCSSAveragePHForPlan = ConvertCssColorForRGB(tvCSSAveragePHForPlan);
        // tvCSSAverageFactOnHour = ConvertCssColorForRGB(tvCSSAverageFactOnHour);
        // tvCSSForecastOnDay = ConvertCssColorForRGB(tvCSSForecastOnDay);

        let dayPlane = unit_line.GetParams(PARAMS_ID.LINE_DAY_PLANE);
        let obj = {
            dayPlane,
    }

        chartID.options.plugins.subtitle.text = SetMakeScoreString(obj);

        chartID.options.animation.duration = 0
        if(firstLoadStatus)
        {
            let len = cChartIDUnit.GetLenght();
            //cDebug.dprint(len);
            if(len > 0)
            {
                if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.KZ))
                {
                    chartID.canvas.parentNode.style.height = '100vh';
                    chartID.canvas.parentNode.style.width = '100vw';
                    cDebug.dprint("Отработал обновление размера для KZ");
                }
                else if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.VRN))
                {
                    //cDebug.dprint(len);
                    if(len === 1)
                    {
                        chartID.canvas.parentNode.style.height = '100vh';
                        chartID.canvas.parentNode.style.width = '100vw';
                        cDebug.dprint("Отработал обновление размера для 1");
                    }
                    else if(len === 2)
                    {
                        chartID.canvas.parentNode.style.height = '50vh';
                        chartID.canvas.parentNode.style.width = '100vw';
                        cDebug.dprint("Отработал обновление размера для 2");
                    }
                    else if(len === 3) //
                    {
                        //let buffLineID = -1;
                        let sizesArr = [
                            [50, 50],
                            [50, 50],
                            [50, 100]
                        ];
                        let buffChartID = cChartIDUnit.GetChartID(lineID); // 1 линия
                        if(buffChartID === chartID)
                        {
                            let chartIndex = cChartIDUnit.GetARRIDFromChartID(buffChartID);
                            if(chartIndex !== -1)
                            {
                                cDebug.dprint(chartIndex);
                                chartID.canvas.parentNode.style.height = `${sizesArr[chartIndex][0]}vh`;
                                chartID.canvas.parentNode.style.width = `${sizesArr[chartIndex][1]}vw`;
                            }
                            else
                            {
                                Error("Error Size for triple graf! ");
                            }
                        }
                        cDebug.dprint("Отработал обновление размера для 3");
                    }
                    else if(len === 4)
                    {
                        chartID.canvas.parentNode.style.height = '50vh';
                        chartID.canvas.parentNode.style.width = '50vw';
                        cDebug.dprint("Отработал обновление размера для 4");
                    }
                    else return Error("Count of Grafics > 4!");
                }
                else if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.ALL))
                {
                    chartID.canvas.parentNode.style.height = '50vh';
                    chartID.canvas.parentNode.style.width = '100vw';
                    cDebug.dprint("Отработал обновление размера для ALL");
                }
            }
        }
        cUpdatedInfoUnit.AddStats(lineID);
        window.addEventListener('afterprint', () => {
            chartID.resize();
        });

        chartID.update();
    }
}

$(document).ready(function()
{
    let htmlType = document.getElementById('html_type').textContent;
    cHTMLType.setType(htmlType);


    if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.KZ))
    {
        document.getElementById('lines_count_one').style.display = 'none';
    }
    else if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.VRN))
    {
        document.getElementById('lines_count_one').style.display = 'none';
        document.getElementById('lines_count_two').style.display = 'none';
        document.getElementById('lines_count_tris').style.display = 'none';
        document.getElementById('lines_count_fours').style.display = 'none';
    }
    else if(cHTMLType.isCurrentShowType(CLineShowType.SHOW_TYPES.ALL))
    {
        document.getElementById('lines_count_five').style.display = 'none';
    }
    document.getElementById('getdate_dialog').style.display = 'block';

	setTimeout(FirstLoadAfterDelay, 500);

}); // document ready