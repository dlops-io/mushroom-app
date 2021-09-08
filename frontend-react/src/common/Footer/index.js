import React, { useEffect, useRef, useState } from 'react';
import { withStyles } from '@material-ui/core';

import styles from './styles';

const Footer = (props) => {
    const { classes } = props;
    const { history } = props;

    console.log("================================== Footer ======================================");

    // Component States

    // Setup Component
    useEffect(() => {

    }, []);

    return (
        <div className={classes.root}>

        </div>
    );
};

export default withStyles(styles)(Footer);