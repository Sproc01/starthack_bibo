import React from 'react';
import { useTheme } from '@mui/material/styles';
import { Gauge, gaugeClasses  } from '@mui/x-charts/Gauge';
import { Alert, Grid2} from '@mui/material';

function getRandomInt(min: number,max: number) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function convertRiskToGauges(risk: number) {
    let gauge = risk/9 * 100;
    return gauge;
}

function addDays(date:Date, days:number) {
    var result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

function GaugeComponent({ risk, week_index }: { risk: number, week_index: number }) {
    const theme = useTheme();
    let settings = {
        startAngle:-100,
        endAngle: 100,
        innerRadius: "80%",
        outerRadius:"100%"
    };

    let AlertBlock = <div className='alertBox'></div>;
    let color = theme.palette.success.main;
    if (risk > 3 && risk <= 6) {
        color = theme.palette.warning.main;
        AlertBlock = <div className='alertBox'>
            <Alert variant="filled" severity="warning" sx={{ padding: '0px 16px' }}>
                Placeholder warning
            </Alert>
        </div>
    } else if (risk > 6) {
        color = theme.palette.error.main;
        AlertBlock = <div className='alertBox'>
            <Alert variant="filled" severity="error" sx={{ padding: '0px 16px' }}>
                Placeholder alert
            </Alert>
        </div>
    }

    const curr = new Date(); // get current date
    const week_day = addDays(curr, week_index*7);
    const last_week_day = addDays(week_day, 6);


         
    return <div className='gauge'>
        {AlertBlock}
        <Gauge
            {...settings}
            value={convertRiskToGauges(risk)}
            text={`${risk} / 9`}
            sx={(theme) => ({
                [`& .${gaugeClasses.valueText}`]: {
                fontSize: 30,
                },
                [`& .${gaugeClasses.valueArc}`]: {
                fill: color,
                },
            })}
        />
        <span>{week_day.getDate()}/{week_day.getMonth()} - {last_week_day.getDate()}/{last_week_day.getMonth()}</span>
    </div>
}

function Gauges() {
    let mock_data:number[] = []
    for (let i = 0; i < 12; i++) {
        mock_data.push(getRandomInt(0, 9));
    }
    let i = 0;
    return (
        <div>
            <Grid2 container spacing={0} height={'70vh'}>
                {mock_data.map(risk =>
                    <Grid2 size={{ xs: 6, sm: 3 }} padding={2}>
                        <GaugeComponent risk = {risk} week_index = {i++}/>
                    </Grid2>
                )}
            </Grid2>
        </div>
    );
};

export default Gauges;