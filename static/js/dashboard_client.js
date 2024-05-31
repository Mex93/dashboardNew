

let lines_selected = undefined
let htmlType = undefined

class LineStats
{
    lineID = undefined;
    hoursPoints_X = null
    hoursPoints_Y = null
    fiveMinsPoints_X = undefined;
    fiveMinsPoints_Y = undefined;
    dayPlane = undefined;
    dayPlanePHSpeed = undefined;
    //
    factDayTotal = undefined;
    speedPH = undefined;
    dayForecast = undefined;

    static classUnits = []
    static linesResponse = []

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

        LineStats.classUnits.push(this)

    }
    getUnitID()
    {
        return this;
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
                    return true;
                }
            }
        }
        return false;
    }
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
                    return true;
                }
            }
        }
        return false;
    }

    addResponseForLine = () => LineStats.linesResponse.push(this);

    updateDayPlaneTotal = (dValue) => this.dayPlane = dValue;
    updateDayPlaneSpeed = (dValue) => this.dayPlanePHSpeed = dValue;
    updatFactDayTotal = (dValue) => this.factDayTotal = dValue;
    updatFactDaySpeed = (dValue) => this.speedPH = dValue;
    updatDayForecast = (dValue) => this.dayForecast = dValue;
    getLineID = () => this.lineID;

}

function getLinesData()
{
    console.log(lines_selected)
    if (Array.isArray(lines_selected))
    {
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
                        let lineID = data[4];

                        let unitID;
                        if(!LineStats.isLineCreated(lineID))
                        {
                            unitID = new LineStats(lineID);

                            unitID.addResponseForLine(lineID);
                        }
                        else
                        {
                            unitID = LineStats.getUnitFromLineID(lineID)
                        }

                        let lineCoords = data[0];
                        //
                        let hoursPoints = lineCoords[0]
                        let fiveMinsPoints = lineCoords[1]
                        let dayPlane = lineCoords[2]
                        let dayPlanePHSpeed = lineCoords[3]
                        //
                        let factDayTotal = data[1];
                        let speedPH = data[2];
                        let dayForecast = data[3];

                        unitID.updateDayPlaneTotal(dayPlane);
                        unitID.updatDayForecast(dayForecast);
                        unitID.updatFactDaySpeed(speedPH);
                        unitID.updatFactDayTotal(factDayTotal);
                        unitID.updateDayPlaneSpeed(dayPlanePHSpeed);

                        unitID.updateFiveMinsPoints(fiveMinsPoints);
                        unitID.updateHoursPoints(hoursPoints);
                    }
                }
            );
        })
    }
}










$(document).ready(function()
{
    let lines = document.getElementById('lines_selected').textContent;
    lines_selected = lines.split(",")
    document.getElementById('lines_count_one').style.display = 'none';
    document.getElementById('lines_count_two').style.display = 'none';
    document.getElementById('lines_count_tris').style.display = 'none';
    document.getElementById('lines_count_fours').style.display = 'none';
    document.getElementById('lines_count_five').style.display = 'none';

    //
	setTimeout(getLinesData, 500);

}); // document ready