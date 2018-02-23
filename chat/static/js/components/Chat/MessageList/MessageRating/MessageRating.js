import React from 'react';
import Rating from 'react-rating';
import styles from './MessageRating.css'

export default class MessageRating extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
        this.state = {
            rating: this.props.current,
            open: typeof(this.props.open) !== 'undefined' ? this.props.open : true
        };
        this.toggleOpen = this.toggleOpen.bind(this);
    }

    rate(value) {
        let props = this.props;
        this.setState({rating: parseFloat(value)});
        $.ajax({
            url: props.url,
            data: {
                reward: value
            },
            headers: {
                'X-CSRFToken': this.props.csrfToken
            },
            method: 'PATCH',
            datatype: 'json',
            cache: false
        });
    }

    toggleOpen(event) {
        event.preventDefault();
        this.setState({
            open: !this.state.open
        })
    }

    render() {
        return (
            <div className={styles.container} data-open={this.state.open}>
                <span className={styles["rate-prompt"]} onClick={this.toggleOpen}>
                </span>
                <div className={styles.rating}>
                    <span className={styles.name}>{this.props.name}:</span>
                    <Rating initialRating={this.state.rating}
                            start={0}
                            stop={1}
                            fractions={2}
                            step={.2}
                            onChange={this.rate.bind(this)}
                            emptySymbol={styles["star-empty"]}
                            fullSymbol={styles["star-full"]}/>
                </div>
            </div>
        )
    }
}