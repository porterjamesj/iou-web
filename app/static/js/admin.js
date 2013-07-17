/* globals $SCRIPT_ROOT, $ */

;(function(exports) {

  var addTrans = function(group_id,amount,from,to_id,kind) {
    $.ajax({
      method: "POST",
      contentType: "application/json",
      url: $SCRIPT_ROOT + "/add",
      data: JSON.stringify({"group_id":group_id,
                            "from":from, //an array
                            "to_id":to_id,
                            "amount": amount,
                            "kind":kind})
    });
  };

  var getGroup = function($button) {
    /* Figure out which group a button belongs to. */
    var groupid = $button.closest("[group]").attr("group");
    return parseInt(groupid,10);
  };

  var getTransType =  function($button) {
    /* Figure out whether a button is for a debt or a payment */
     return $button.closest("[transtype]").attr("transtype");
  };

  var getTag = function($button,tag) {
    /* Get the user ids of the buttons matching a tag. */
    var userids = $button.closest("[transtype]")
      .find("[tag=" + tag +"]")
      .find("button.active")
      .map(function () { return this.getAttribute("uid"); })
      .get();

    return _.map(userids,function (uid) { return parseInt(uid,10); });
  };

  var getField = function($button,field) {
     return $button.closest("[transtype]")
      .find("input[name=" + field + "]")
      .val();
  };

  var submit = function(button) {
    $button = $(button);
    group = getGroup($button);
    debtors = getTag($button,"from");
    creditors = getTag($button,"to");
    amount = parseInt(getField($button,"amount"),10);
    transtype = getTransType($button);
    if (transtype === "debt") { // This is a debt
      addTrans(group,amount,debtors,creditors,transtype);
    } else { // This is a payment, have to reverse the logic
      addTrans(group,amount,creditors,debtors,transtype);
    }
  };

  var clearAll = function(button) {
    $button = $(button);
    group = getGroup($button);
    $.ajax({
      method: "POST",
      contentType: "application/json",
      url: $SCRIPT_ROOT + "/clearall/" + group,
    });
  };

  var addAdmins = function(button) {
    $button = $(button);
    group = getGroup($button);
    user = getTag($button,"user");
    $.ajax({
      method:"POST",
      contentType: "application/json",
      url: $SCRIPT_ROOT + "/addadmin",
      data: JSON.stringify({"user": user,
                            "group": group})
      });
  };

  var resign = function(button) {
    $button = $(button);
    group = getGroup($button);
    $.ajax({
      method:"POST",
      contentType: "application/json",
      url: $SCRIPT_ROOT + "/resign/" + group,
      success: window.location.reload()
    })
  };

  var appendUsers = function($button,data) {
    users = data['users'];
    $button.siblings(".user").remove()
    _.map(users, function(user) {
      if (user.groups.indexOf(getGroup($button)) == -1) {
        $button.parent().append("<a style='display:block' class='user' uid="
                                + user.id + " href='#'>"
                                + user.email + " (" + user.name + ")"+
                                "</a>");
      }
    });
  };

  var searchUsers = function(button) {
    $button = $(button);
    querystring = getField($button,"search");
    $.ajax({
      method:"POST",
      contentType: "application/json",
      url: $SCRIPT_ROOT + "/search/users/" + querystring,
      success: function (data) { appendUsers($button,data); }
    });
  };

  exports.addEventListeners = function() {
    $("button[role=submit]").click(function() { submit(this); });
    $("button[role=clearall]").click(function() { clearAll(this); });
    $("button[role=addadmin]").click(function() { addAdmins(this); });
    $("button[role=resign]").click(function() { resign(this); });
    $("button[role=search]").click(function() { searchUsers(this); });
  };

})(this);

$(function () {
  addEventListeners();
});
