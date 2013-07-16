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

  var getAmount = function($button) {
    var amount = $button.closest("[transtype]")
      .find("input[name=amount]")
      .val();
    return parseInt(amount,10);
  };

  var submit = function(button) {
    $button = $(button);
    group = getGroup($button);
    debtors = getTag($button,"from");
    creditors = getTag($button,"to");
    amount = getAmount($button);
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

  exports.addEventListeners = function() {
    $("button[role=submit]").click(function() { submit(this); });
    $("button[role=clearall]").click(function() { clearAll(this); });
    $("button[role=addadmin]").click(function() { addAdmins(this); });
  };

})(this);

$(function () {
  addEventListeners();
});
