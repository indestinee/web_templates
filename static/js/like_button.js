class NameForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {value: '', msg: '- -'};

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        const {value} = this.state;
        alert('A name was submitted: ' + value);
        fetch('/login', {
            method: 'POST',

            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                firstParam: 'yourValue',
                secondParam: value,
            }) 
        })
        .then(res => res.json())
        .then(
            (result) => {
                alert('suc');
                this.setState({
                    items: result.items
                });
            },
            (error) => {
                alert('err');
                this.setState({
                    msg: ':(',
                    error
                });

            }
        )
    }

    render() {
        var msg = this.state.msg;
        return (
            <form onSubmit={this.handleSubmit}>
            <label>
            Name:
            <input type="text" value={this.state.value} onChange={this.handleChange} />
            </label>
            {msg}
            <input type="submit" value="Submit" />
            </form>
        );
    }
}

ReactDOM.render(
    <NameForm />,
    document.getElementById('funny')
);
