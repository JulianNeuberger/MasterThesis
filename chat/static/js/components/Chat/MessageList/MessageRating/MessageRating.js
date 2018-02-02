import React from 'react';
import Rating from 'react-rating';
// import styles from 'MessageRating.css'
// import 'font-awesome-webpack';

export default class MessageRating extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
        this.state = {
            rating: this.props.current,
        };
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

    render() {
        return (
            <div>
                {this.props.name}:
                <Rating initialRating={this.state.rating}
                        start={0}
                        stop={1}
                        fractions={2}
                        step={.2}
                        onChange={this.rate.bind(this)}
                        // emptySymbol={styles.}
                        // fullSymbol={"fas fa-star"}
                />
            </div>
        )
    }
}