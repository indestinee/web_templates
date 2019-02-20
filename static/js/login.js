import '../css/signup.css';

class Content extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <form className="form-signin" action="servlet" method="post" onsubmit="return submit_form();">
      <h1 className="h3 mb-3 font-weight-normal">Sign Up</h1>
      <label for="nickname" className="sr-only">Nickname</label>
      <input type="nickname" name="nickname" id="nickname" className="form-control" placeholder="Nickname" required autofocus/>
      <label for="username" className="sr-only">Username</label>
      <input type="username" name="username" id="username" className="form-control" placeholder="Username" required autofocus/>
      <label for="password" className="sr-only">Password</label>
      <input type="password" name="password" id="password" className="form-control" placeholder="Password" required/>

      <label for="code" className="sr-only">Invitation Code</label>
      <input type="code" name="code" id="code" className="form-control" placeholder="Invitation Code" autofocus/>
      <div className="checkbox mb-3">
      <label>
      <input type="checkbox" id="login" checked/> Sign In after Register
      </label>
      </div>
      <div id="msg" className="msg"></div>
      <button className="btn btn-lg btn-primary btn-block" type="submit">Sign Up</button>
      <br/>
      <p align="right">Already had a account? <a href="/login">Sign In</a></p>
      </form>
    );
  }
}
const element = <Content/>;
ReactDOM.render(
  element,
  document.getElementById('example')
);
