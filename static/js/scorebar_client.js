function getrdata()
{
	return Math.floor((Math.random() * 100) + 1);
}
function first_load()
{
   getdata();
}


let updateTicks = 13



function findWord(str, word) {
    return str.includes(word)
}
function getdata()
{
        let h1_TV = 0;
        let m5_TV = 0;
        let forecast_TV = 0;
        let av_speed = 0;
        let checked_data = 0;

        let line_id = document.getElementById('line_id').textContent;
//        console.log(line_id)
//        console.log(country_id)

        //var json_text = '{ "line_id": "{{ line_id }}","panel": "scoreboard"}';
        let json_text = '{"cline_id": "'+ line_id +'"}';
        let completed_json = jQuery.parseJSON(json_text);

        $.getJSON('/engine_scripts/py/launch_scripts/scoreboard_get_stats.py', completed_json, function (data)
        {
            checked_data = data["checked_data"];
            console.log(data)
            if(findWord(data["error"], "All Data Stored"))
            {
                //console.log(data);
                //alert(data["display_name"]);
                document.title = data["title"];
                line_id = +data["line_id"];

                //console.log(data["ctime"])

                $("#name").text(data["name"]);
                $("#shift_plan").text(data["plan"]);
                $("#tv_count").text(data["TV"]);

                $("#opt_speed_for_shift").text(data["opt_speed"]);
                $("#opt_speed_for_shift").removeClass().addClass('value' + data["opt_speed_for_shift_css"]);

                $("#average_speed").text(data["av_speed"]);
                $("#average_speed").removeClass().addClass('value' + data["av_speed_css"]);
                av_speed = +data["av_speed"];

                $("#tv_per_last_hour").text(data["h1_TV"]);
                $("#tv_per_last_hour").removeClass().addClass('value' + data["h1_TV_css"]);
                h1_TV = +data["h1_TV"];

                $("#tv_per_last_5min").text(data["m5_TV"]);
                $("#tv_per_last_5min").removeClass().addClass('value' + data["m5_TV_css"]);
                m5_TV = +data["m5_TV"];

                $("#tv_forecast_total").text(data["forecast_TV"]);
                $("#tv_forecast_total").removeClass().addClass('value' + data["tv_forecast_total_css"]);
                forecast_TV = +data["forecast_TV"];

                let minutes = +data["time_mins"];
                let hours = +data["time_hours"];

                $("#min").html(( minutes < 10 ? "0" : "" ) + minutes);
                $("#hours").html(( hours < 10 ? "0" : "" ) + hours);

                console.log("Данные обновлены")

                updateTicks = 13;

            }
            else
            {
                $("#status").text(data["error"]);
            }

            if(checked_data !== 0) // работает только после получения JSON ответа от скрипта
            {
                $("#status").text(data["status_txt"]);
                // оставил просто впадлу удалять
            }
            else $("#status").text('Ошибка получения данных!');
        }
        );


}
Date.prototype.getUTCTime = function()
{
    return this.getTime()-(this.getTimezoneOffset()*60000);
};
$(document).ready(function() {

	document.title = 'Статистика Цех: ~';
	 $("#name").text('-');
	 $("#shift_plan").text('-');
	 $("#tv_count").text('-');
	 $("#opt_speed_for_shift").text('-');
	 $("#average_speed").text('-');
	 $("#tv_per_last_hour").text('-');
	 $("#tv_per_last_5min").text('-');
	 $("#tv_forecast_total").text('-');

	$("#status").text('Получение данных...');
	setTimeout(first_load, 1300);

    // $("#min").html(( minutes < 10 ? "0" : "" ) + minutes);
    // $("#hours").html(( hours < 10 ? "0" : "" ) + hours);

	setInterval( function()
	{
		getdata();
	},
	13*1000);

    setInterval( function()
        {
            if(updateTicks !== -1)
            {
                updateTicks --;
                if (updateTicks < 0)
                {
                    updateTicks = -1;
                }
            }
            else
            {
                $("#min").html("-");
                $("#hours").html("-");
                $("#status").text('Получение данных...');
            }
        },
        1000);

}); // document ready