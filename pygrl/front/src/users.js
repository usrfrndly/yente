var UserBox = React.createClass({
  getInitialState: function () {
    return {data: []};
  },
  componentDidMount: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function () {
    return (
      <div className="userBox">
        <UserList data={this.state.data} />
      </div>
    );
  }
});

var UserList = React.createClass({
  render: function () {
    var userNodes = this.props.data.map(function (user) {
      return (
        <li>
          <User data={user} key={user.id} />
        </li>
        );
    });
    return (
      <div className="userList">
        <h1>Users</h1>
        <ul className="container">
          {userNodes}
        </ul>
      </div>
    );
  }
});

var User = React.createClass({
  render: function () {
    var photos = this.props.data.photos.map(function (url) {
      return (
        <img src={url}></img>
        )
    });
    return (
      <div className="user row">
        <div className="details col-md-3">
          <h2>{this.props.data.name} ({this.props.data.age})</h2>
          <p>{this.props.data.bio}</p>
        </div>
        <div className="photos col-md-9">
          {photos}
        </div>
      </div>
    );
  }
});


React.render(
  <UserBox url="/users" />,
  document.getElementById('content')
);
