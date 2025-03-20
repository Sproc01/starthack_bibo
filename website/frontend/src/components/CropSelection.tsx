import React from 'react';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

function CropSelection() {
	const [crop, setCrop] = React.useState<string | null>('soybean');

	const handleChange = (
	  event: React.MouseEvent<HTMLElement>,
	  newCrop: string | null,
	) => {
		if (newCrop === null) {
			return;
		}
		setCrop(newCrop);
	};


	return (
		<>
			<ToggleButtonGroup
				color="primary"
				value={crop}
				exclusive
				onChange={handleChange}
				aria-label="text alignment"
				>
				<ToggleButton value="soybean">
					Soybean
				</ToggleButton>
				<ToggleButton value="corn">
					Corn
				</ToggleButton>
				<ToggleButton value="cotton">
					Cotton
				</ToggleButton>
				<ToggleButton value="rice">
					Rice
				</ToggleButton>
				<ToggleButton value="wheat">
					Wheat
				</ToggleButton>
			</ToggleButtonGroup>
		</>
	);
};

export default CropSelection;