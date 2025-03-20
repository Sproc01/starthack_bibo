import React from 'react';
import { useTheme } from '@mui/material/styles';
import { Gauge, gaugeClasses  } from '@mui/x-charts/Gauge';
import { Alert, Grid2, Paper} from '@mui/material';

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
                Stress warning!
            </Alert>
        </div>
    } else if (risk > 6) {
        color = theme.palette.error.main;
        AlertBlock = <div className='alertBox'>
            <Alert variant="filled" severity="error" sx={{ padding: '0px 16px' }}>
                Stress alert!
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

function monthGauges({stress, start_index }: {stress: number[], start_index: number}) {
    let list_of_gauges = []
    for(let i = start_index; i < start_index + 4; i++) {
        let risk = stress[i];
        list_of_gauges.push(<Grid2 size={{ xs: 12, sm: 3 }} padding={2} minHeight={'200px'} height={'28vh'}>
            <GaugeComponent risk = {risk} week_index = {i}/>
        </Grid2>)
    }
    return <Paper elevation={2} sx={{margin: '1vh'}}>
        <Grid2 container spacing={0}>
            {list_of_gauges}
        </Grid2>
    </Paper>;
}

function Gauges({stress, labels}: {stress: number[], labels: string[]}) {
    

    return (
        <div>
            {monthGauges({stress, start_index: 0})}
            {monthGauges({stress, start_index: 4})}
            {monthGauges({stress, start_index: 8})}
        </div>
    );
};

export default Gauges;