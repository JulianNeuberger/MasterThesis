import React from "react";
import styles from './Controls.css'
import Button from "./Buttons/Button";

export default class Controls extends React.Component {
    constructor(props) {
        super();
        this.props = props;
    }


    render() {
        return (
            <span>
                <div className={styles.container}>
                    <Button csrfToken={this.props.csrfToken}
                            statusUrl={this.props.trainStatusUrl}
                            statusParams={{}}
                            statusKey='training'
                            actionName='training'
                            iconUrl='/static/img/brain-gear.svg'
                            actionUrl={this.props.trainActionUrl}
                            pollInterval={this.props.pollInterval}
                            runningStyle={styles.turning}
                            normalStyle={styles.normal}>
                        train
                    </Button>
                    <Button csrfToken={this.props.csrfToken}
                            statusUrl={this.props.saveStatusUrl}
                            statusParams={{}}
                            statusKey='saving'
                            actionName='saving'
                            iconUrl='/static/img/floppy-solid.svg'
                            actionUrl={this.props.saveActionurl}
                            pollInterval={this.props.pollInterval}
                            runningStyle={styles.normal}
                            normalStyle={styles.normal}>
                        save
                    </Button>
                </div>
            </span>
        );
    }
}