import {
    getIntervalArr, getRandomInt,
    GetStandartFMinsAssocArr,
    getStandartPHMainLandArr,
    SetMakeScoreString
} from "./libs/dashboard/utils.js";




let lines_selected = undefined;
let mainDIV = undefined;
let debugMode = false;
let resizeCompleted = false;

class LineStats
{
    lineID = undefined;
    hoursPoints_X = null
    hoursPoints_Y = null
    hoursPointsArr = null
    fiveMinsPoints_X = undefined;
    fiveMinsPoints_Y = undefined;
    fiveMinsPointsArr = undefined;
    dayPlane = undefined;
    dayPlanePHSpeed = undefined;
    //
    factDayTotal = undefined;
    speedPH = undefined;
    dayForecast = undefined;

    canvasID = undefined;
    chartID = undefined;
    ID = undefined;

    static classUnits = [];
    static linesResponse = [];
    static count = 0;
    constructor(lineID)
    {
       this.lineID = lineID
       this.hoursPoints_X = null
       this.hoursPoints_Y = null
       this.fiveMinsPoints_X = undefined;
       this.fiveMinsPoints_Y = undefined;
       this.dayPlane = undefined;
       this.dayPlanePHSpeed = undefined;
        //
       this.factDayTotal = undefined;
       this.speedPH = undefined;
       this.dayForecast = undefined;
       this.canvasID = 'none'

        this.ID = LineStats.count;
        LineStats.count++;

        LineStats.classUnits.push(this)
    }
    getID = () => this.ID;
    setCanvasID = (cID) => this.canvasID = cID;
    getCanvasID = () => this.canvasID;

    setChartID = (cID) => this.chartID = cID;
    getChartID = () => this.chartID;

    getLineName()
    {
        return `Линия №:${this.lineID}`;
    }
    static getUnitFromLineID(findLineID)
    {
        let len = LineStats.classUnits.length;
        if (len > 0)
        {
            for(let i = 0; i < len; i++)
            {
                let unitID = LineStats.classUnits[i];
                let LineID = unitID.getLineID();
                if (LineID === findLineID)
                {
                    return unitID;
                }
            }
        }
        return null;
    }
    static isLineCreated(flineID)
    {
        let len = LineStats.classUnits.length;
        if (len > 0)
        {
            for(let i = 0; i < len; i++)
            {
                let unitID = LineStats.classUnits[i];
                let cLineID = unitID.getLineID();
                if (cLineID === flineID)
                {
                    return true;
                }
            }
        }
        return false;
    }
    static getActiveLinesList()
    {
        return LineStats.classUnits;
    }


    updateHoursPoints(hPoints)
    {
        if(hPoints instanceof Object)
        {
            let hoursPoints_X = Object.keys(hPoints);
            if(Array.isArray(hoursPoints_X))
            {
                let hoursPoints_Y = Object.values(hPoints);
                if(Array.isArray(hoursPoints_Y))
                {
                    this.hoursPoints_X = hoursPoints_X;
                    this.hoursPoints_Y = hoursPoints_Y;
                    this.hoursPointsArr = Object.entries(hPoints);
                    return true;
                }
            }
        }
        return false;
    }
    getHoursPoints = () => this.hoursPointsArr

    updateFiveMinsPoints(fPoints)
    {
        if(fPoints instanceof Object)
        {
            let fiveMinsPoints_X = Object.keys(fPoints);
            if(Array.isArray(fiveMinsPoints_X))
            {
                let fiveMinsPoints_Y = Object.values(fPoints);
                if(Array.isArray(fiveMinsPoints_Y))
                {
                    this.fiveMinsPoints_X = fiveMinsPoints_X;
                    this.fiveMinsPoints_Y = fiveMinsPoints_Y;
                    this.fiveMinsPointsArr = Object.entries(fPoints);
                    return true;
                }
            }
        }
        return false;
    }

    getFiveMinsPoints = () => this.fiveMinsPointsArr;

    addResponseForLine = () => LineStats.linesResponse.push(this);

    updateDayPlaneTotal = (dValue) => this.dayPlane = dValue;
    getDayPlaneTotal = () => this.dayPlane;
    updateDayPlaneSpeed = (dValue) => this.dayPlanePHSpeed = dValue;
    getDayPlaneSpeed = () => this.dayPlanePHSpeed;
    updatFactDayTotal = (dValue) => this.factDayTotal = dValue;
    getFactDayTotal = () => this.factDayTotal;
    updatFactDaySpeed = (dValue) => this.speedPH = dValue;
    getFactDaySpeed = () => this.speedPH;
    updatDayForecast = (dValue) => this.dayForecast = dValue;
    getDayForecast = () => this.dayForecast;
    getLineID = () => this.lineID;

}

function getLinesData()
{
    if (Array.isArray(lines_selected))
    {
        console.log(lines_selected)
        lines_selected.forEach( (lineID) =>
        {
            let json_text = '{"line_id": "'+ lineID +'"}';

            let completed_json = jQuery.parseJSON(json_text);
            $.getJSON('/engine_scripts/py/launch_scripts/dashboard_get_stats.py',
                completed_json, function (data)
                {
                    // console.log(data)
                    if(Array.isArray(data))
                    {
                        //console.log(data)
                        //
                        let unitID = null;
                        let hoursPoints = null;
                        let fiveMinsPoints = null;

                        let dayPlanePHSpeed = null;
                        //
                        let factDayTotal = null;
                        let speedPH = null;
                        let dayForecast = null;
                        let isCreated = null;
                        let dayPlane = null;
                        if(debugMode === false)
                        {
                            let lineStats = data[0];
                            dayPlane = lineStats[2]
                            //console.log(dayPlane)
                            let lineID = data[4];
                            if(dayPlane === 777)
                            {
                                if(resizeCompleted) // если не первичный запуск
                                {
                                    // Если график создан и пришёл пустой ответ от линии = перезапускаем
                                    if(LineStats.isLineCreated(lineID))
                                    {
                                        location.reload();
                                        return
                                    }
                                }
                            }
                            if(dayPlane !== 777 && dayPlane != null)  //if(dayPlane === 777)
                            {
                                // Если не ноль и не 777 (отсутствуют поинты для построения)
                                isCreated = LineStats.isLineCreated(lineID);
                                if(!isCreated)
                                {
                                    if(resizeCompleted)
                                    {

                                        location.reload();
                                        return
                                    }

                                    unitID = new LineStats(lineID);
                                    unitID.addResponseForLine(lineID);

                                }
                                else
                                {
                                    unitID = LineStats.getUnitFromLineID(lineID)
                                }
                                //

                                hoursPoints = lineStats[0]
                                fiveMinsPoints = lineStats[1]

                                dayPlanePHSpeed = lineStats[3];
                                //
                                factDayTotal = data[1];
                                speedPH = data[2];
                                dayForecast = data[3];
                            }
                            else
                            {
                                return false;
                            }
                        }
                        else
                        {
                            isCreated = LineStats.isLineCreated(lineID);
                            if(!isCreated)
                            {
                                unitID = new LineStats(lineID);

                                unitID.addResponseForLine(lineID);

                            }
                            else
                            {
                                unitID = LineStats.getUnitFromLineID(lineID)
                            }

                            hoursPoints = {
                                "10": 126,
                                "11": 144,
                                "12": 66,
                                "13": 131,
                                "14": 154,
                                "15": 123,
                                "16": 53,
                                "08": 118,
                                "09": 142
                            }

                            fiveMinsPoints = {
                                "08:00": 72,
                                "08:05": 108,
                                "08:10": 60,
                                "08:15": 156,
                                "08:20": 120,
                                "08:25": 120,
                                "08:30": 108,
                                "08:35": 156,
                                "08:40": 144,
                                "08:45": 120,
                                "08:50": 132,
                                "08:55": 120,
                                "09:00": 132,
                                "09:05": 124,
                                "09:10": 130,
                                "09:15": 134,
                                "09:20": 127,
                                "09:25": 131,
                                "09:30": 136,
                                "09:35": 137,
                                "09:40": 138,
                                "09:45": 137,
                                "09:50": 140,
                                "09:55": 141,
                                "10:00": 0,
                                "10:05": 0,
                                "10:10": 142,
                                "10:15": 141,
                                "10:20": 141,
                                "10:25": 144,
                                "10:30": 152,
                                "10:35": 150,
                                "10:40": 147,
                                "10:45": 148,
                                "10:50": 146,
                                "10:55": 149,
                                "11:00": 149,
                                "11:05": 151,
                                "11:10": 151,
                                "11:15": 154,
                                "11:20": 149,
                                "11:25": 151,
                                "11:30": 151,
                                "11:35": 153,
                                "11:40": 144,
                                "11:45": 141,
                                "11:50": 143,
                                "11:55": 144,
                                "12:00": 144,
                                "12:05": 145,
                                "12:10": 149,
                                "12:15": 145,
                                "12:20": 150,
                                "12:25": 0,
                                "12:30": 0,
                                "12:35": 0,
                                "12:40": 0,
                                "12:45": 0,
                                "12:50": 0,
                                "12:55": 0,
                                "13:00": 0,
                                "13:05": 147,
                                "13:10": 144,
                                "13:15": 143,
                                "13:20": 152,
                                "13:25": 157,
                                "13:30": 155,
                                "13:35": 152,
                                "13:40": 152,
                                "13:45": 145,
                                "13:50": 142,
                                "13:55": 145,
                                "14:00": 142,
                                "14:05": 143,
                                "14:10": 147,
                                "14:15": 148,
                                "14:20": 147,
                                "14:25": 150,
                                "14:30": 152,
                                "14:35": 154,
                                "14:40": 152,
                                "14:45": 156,
                                "14:50": 151,
                                "14:55": 157,
                                "15:00": 0,
                                "15:05": 0,
                                "15:10": 154,
                                "15:15": 153,
                                "15:20": 148,
                                "15:25": 147,
                                "15:30": 149,
                                "15:35": 146,
                                "15:40": 143,
                                "15:45": 142,
                                "15:50": 145,
                                "15:55": 144,
                                "16:00": 151,
                                "16:05": 146,
                                "16:10": 152,
                                "16:15": 154
                            }

                            dayPlanePHSpeed = getRandomInt(900+200)
                            //
                            factDayTotal = getRandomInt(900+200);
                            speedPH = getRandomInt(900+200);
                            dayForecast = getRandomInt(900+200);
                            dayPlane = getRandomInt(900+200);
                        }
                        if(unitID !== null)
                        {
                            unitID.updateDayPlaneTotal(dayPlane);
                            unitID.updatDayForecast(dayForecast);
                            unitID.updatFactDaySpeed(speedPH);
                            unitID.updatFactDayTotal(factDayTotal);
                            unitID.updateDayPlaneSpeed(dayPlanePHSpeed);

                            unitID.updateFiveMinsPoints(fiveMinsPoints);
                            unitID.updateHoursPoints(hoursPoints);

                            StoredData(unitID, isCreated)
                        }

                    }
                }
            );

        })
    }
}
function UpdateFunc()
{
    let arr = LineStats.getActiveLinesList();
    if(Array.isArray(arr) && arr.length > 0)
    {
        getLinesData();
    }
}
function resizeGraph()
{
    let lines = LineStats.getActiveLinesList();

    let len = lines.length;
    //cDebug.dprint(len);

    if(len > 0)
    {
        //cDebug.dprint(len);
        for(let unitID of lines)
        {
            let chartID = unitID.getChartID();
            let canvasID = unitID.getCanvasID();
            if (len === 1)
            {
                canvasID.style.height = '100vh';
                canvasID.style.width = '100vw';
                cDebug.dprint("Отработал обновление размера для 1");
            }
            else if(len === 2)
            {
                canvasID.style.height = '50vh';
                canvasID.style.width = '100vw';
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
                let ID = unitID.getID();
                canvasID.style.height = `${sizesArr[ID][0]}vh`;
                canvasID.style.width = `${sizesArr[ID][1]}vw`;

                cDebug.dprint("Отработал обновление размера для 3");
            }
            else if(len === 4)
            {
                canvasID.style.height = '50vh';
                canvasID.style.width = '50vw';
                cDebug.dprint("Отработал обновление размера для 4");
            }
            else
            {
                canvasID.style.height = '50vh';
                canvasID.style.width = '100vw';
                cDebug.dprint("Отработал обновление размера для ALL");
            }

            window.addEventListener('afterprint', () => {
                chartID.resize();
            });

            chartID.update();
        }
        // div and blocks
        if (len === 1)
        {
            let div = document.createElement("div");
            div.className = 'canvas_colors canvas_size_one'

            let canvasID = lines[0].getCanvasID();
            div.append(canvasID);
            mainDIV.append(div)
        }
        else if(len === 2)
        {
            let div = document.createElement("div");
            div.className = 'canvas_colors canvas_size_two'

            for(let unitID of lines)
            {
                let div2 = document.createElement("div");

                let canvasID = unitID.getCanvasID();
                div2.append(canvasID);

                div.append(div2)
            }
            mainDIV.append(div)
        }
        else if(len === 3) //
        {
            let div = document.createElement("div");
            div.className = 'chart-container_tris canvas_colors'

            let cust = [lines[0], lines[1]];

            for(let unitID of cust)
            {
                let div2 = document.createElement("div");
                div2.className = 'chart_unit_tris'
                let canvasID = unitID.getCanvasID();
                div2.append(canvasID);

                div.append(div2)
            }

            let div3 = document.createElement("div");
            div3.className = 'chart_tris_footer canvas_colors'
            let canvasID = lines[2].getCanvasID();
            div3.append(canvasID);
            mainDIV.append(div)
            mainDIV.append(div3)
        }
        else if(len === 4)
        {
            let div = document.createElement("div");
            div.className = 'graff_container_fours canvas_colors'

            let gra_class = [
                'gra_one',
                'gra_two',
                'gra_tri',
                'gra_fours',
            ];

            for(let [index, unitID] of lines.entries())
            {
                let div2 = document.createElement("div");
                div2.className = `${gra_class[index]} canvas_size_four`;
                let canvasID = unitID.getCanvasID();
                div2.append(canvasID);

                div.append(div2)
            }
            mainDIV.append(div)
        }
        else
        {
            let div = document.createElement("div");
            div.className = 'canvas_main_two'

            for(let unitID of lines)
            {
                let div2 = document.createElement("div");
                let canvasID = unitID.getCanvasID();
                div2.append(canvasID);

                div.append(div2)
            }
            mainDIV.append(div)
        }

        resizeCompleted = true;


        // Показываем
        mainDIV.style.display = "block"
    }

}

class cDebug
{
    static onOff = true;
    constructor() {
    }

    static dprint(text)
    {
        if(cDebug.onOff)
        {
            console.log(text)
        }
    }
}



function StoredData(unit_line, isCreated)
{

    // let fiveMinsPointsY = unit_line.getFiveMinsPointsY();
    // let fiveMinsPointsX = unit_line.getFiveMinsPointsX();
    //
    // let hoursPointsY = unit_line.getHoursPointsY();
    // let hoursPointsX = unit_line.getHoursPointsX();


    let lineID = unit_line.getLineID();

   if(!isCreated) // график не создан  - создание
   {
       let canvasID = document.createElement("canvas")
       canvasID.id = `chart_line_${lineID}`;
       unit_line.setCanvasID(canvasID);
   }
   else  // обновляем данные
   {

   }


    // блок данные

    //  TODO линейный график

    let standart_ph_interval_label = getStandartPHMainLandArr();
    //let standart_ph_label = getStandartPHMainLandArrEx();

    let buffName = unit_line.getLineName();

    let fiveMinsAssocArr = unit_line.getFiveMinsPoints();
    let hoursAssocArr = unit_line.getHoursPoints();
    console.log(hoursAssocArr)
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
    let hourPlane = unit_line.getDayPlaneTotal();
    //cDebug.dprint(countOfFiveMinsDots, countOfHoursDots);
    if(countOfFiveMinsDots > 0 || countOfHoursDots > 0)
    {
        // unit_line.SetParams(PARAMS_ID.LINE_DATE_STATUS,
        //     true);

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
        let emptyAssArrWithFiveMins = GetStandartFMinsAssocArr(hoursAssocArr, fiveMinsAssocArr.length);

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


        // Ширина столба для баровых графиков
        barSize = 12;

        hoursDotsArr = Array.from(standart_mins_assoc_array.values())
        hourPlane = unit_line.getDayPlaneSpeed();
    }
    else
    {
        return false;
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

    if(countOfFiveMinsDots)
    {
        pointsFiveMinsArr = pointsFiveMinsArr.map( (element) =>{
            return element[1];
        })
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

    let subtitleColor = '#c2bfbf';
    if(!isCreated)
    {
        let canvasID = unit_line.getCanvasID();
        //cDebug.dprint(currentLen);
        let ctx = canvasID.getContext("2d");
        let chartIDlocal = new Chart( ctx,

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

        unit_line.setChartID(chartIDlocal);
        cDebug.dprint("Создан график LineID " + lineID);

        return lineID;
    }
    else // обновление
    {
        let chartID = unit_line.getChartID();

        chartID.data.datasets = [
            datasets_chart_5mins,
            datasets_chart_ph
        ]
        chartID.data.labels = label_keys;
        chartID.options.plugins.annotation.annotations.label.yMin = hourPlane;
        chartID.options.plugins.annotation.annotations.label.yMax = hourPlane;

        let dayPlane = unit_line.getDayPlaneTotal();
        let dayFact = unit_line.getFactDayTotal();
        let factSpeed = unit_line.getFactDaySpeed();
        let dayForecast = unit_line.getDayForecast();

        let obj = {
            dayPlane,
            dayFact,
            factSpeed,
            dayForecast
        }
        chartID.options.plugins.subtitle.text = SetMakeScoreString(obj);

        chartID.options.animation.duration = 0
        chartID.update();
    }
}


function ReloadPageFunc()
{
    location.reload();
}



$(document).ready(function()
{
    let lines = document.getElementById('lines_selected').textContent;
    lines_selected = lines.split(",")
    //

    mainDIV = document.createElement("div")
    mainDIV.id = 'main_div'
    document.body.append(mainDIV)
	setTimeout(getLinesData, 500);
    setTimeout(ReloadPageFunc, 2_800_000);  // ~ 50 min
    setInterval(UpdateFunc, 20000);
    setTimeout(resizeGraph, 3000);
    mainDIV.style.display = "none"
}); // document ready