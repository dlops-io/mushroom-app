import React, { useEffect, useState } from 'react';
import { Icon, withStyles } from '@material-ui/core';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import Container from '@material-ui/core/Container';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import NumberFormat from "react-number-format";

import DataService from "../../services/DataService";
import styles from './styles';

const Leaderboard = (props) => {
    const { classes } = props;

    console.log("================================== Leaderboard ======================================");

    // Component States
    const [leaderboard, setLeaderboard] = useState([]);
    const loadLeaderboard = () => {
        DataService.GetLeaderboard()
            .then(function (response) {
                setLeaderboard(response.data);
            });
    }

    // Setup Component
    useEffect(() => {
        loadLeaderboard();
    }, []);

    // Handlers
    const handleRefreshClick = () => {
        loadLeaderboard();
    }

    return (
        <div className={classes.root}>
            <main className={classes.main}>
                <Container maxWidth={false} className={classes.container}>
                    <Toolbar className={classes.toolBar}>
                        <Typography variant="h5" gutterBottom>
                            Leaderboard
                        </Typography>
                        <div className={classes.grow} />
                        <IconButton onClick={() => handleRefreshClick()}>
                            <Icon>refresh</Icon>
                        </IconButton>
                    </Toolbar>
                    <Divider />
                    <div className={classes.spacer}></div>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell></TableCell>
                                    <TableCell>User</TableCell>
                                    <TableCell>Model</TableCell>
                                    <TableCell>Trainable Parameters</TableCell>
                                    <TableCell>Training Time (mins)</TableCell>
                                    <TableCell>Loss</TableCell>
                                    <TableCell>Accuracy</TableCell>
                                    <TableCell>Model Size (Mb)</TableCell>
                                    <TableCell>Learning Rate</TableCell>
                                    <TableCell>Batch Size</TableCell>
                                    <TableCell>Epochs</TableCell>
                                    <TableCell>Optimizer</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {leaderboard && leaderboard.map((itm, idx) =>
                                    <TableRow key={idx}>
                                        <TableCell>{idx + 1}</TableCell>
                                        <TableCell>{itm.email}</TableCell>
                                        <TableCell>{itm.model_name}</TableCell>
                                        <TableCell>
                                            <NumberFormat
                                                value={itm.trainable_parameters}
                                                displayType="text"
                                                thousandSeparator={true}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <NumberFormat
                                                value={itm.execution_time}
                                                displayType="text"
                                                decimalSeparator="."
                                                decimalScale={2}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <NumberFormat
                                                value={itm.loss}
                                                displayType="text"
                                                format="####"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <NumberFormat
                                                value={itm.accuracy * 100.00}
                                                displayType="text"
                                                decimalSeparator="."
                                                decimalScale={2}
                                                suffix="%"

                                            />
                                        </TableCell>
                                        <TableCell>
                                            <NumberFormat
                                                value={itm.model_size / 1000000.00}
                                                displayType="text"
                                                decimalSeparator="."
                                                decimalScale={2}

                                            />
                                        </TableCell>
                                        <TableCell>{itm.learning_rate}</TableCell>
                                        <TableCell>{itm.batch_size}</TableCell>
                                        <TableCell>{itm.epochs}</TableCell>
                                        <TableCell>{itm.optimizer}</TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Container>
            </main>
        </div>
    );
};

export default withStyles(styles)(Leaderboard);