import React from 'react';
import Rating from 'react-rating';
import styles from './MessageRating.module.css'

export default class MessageRating extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
        this.ratingChanged = this.ratingChanged.bind(this);
        this.state = {
            value: this.props.initial
        }
    }

    ratingChanged(value) {
        this.props.onRate(this.props.for, value);
        this.setState({value: value});
    }

    render() {
        return (
            <div className={styles.container}>
                <div className={styles.rating}>
                    <span className={styles.name}>
                        {this.props.name}
                    </span>
                    <Rating initialRating={this.state.value}
                            start={0}
                            stop={10}
                            fractions={2}
                            step={2}
                            onChange={this.ratingChanged}
                            emptySymbol={styles["star-empty"]}
                            fullSymbol={styles["star-full"]}/>
                </div>
            </div>
        )
    }
}