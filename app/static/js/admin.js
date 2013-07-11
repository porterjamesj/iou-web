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

  var getFrom = function($button) {
    /* Get the user ids of the "froms" for a submission. */
    var userids = $button.closest("[transtype]")
      .find("[direction=from]")
      .find("button.active")
      .map(function () { return this.getAttribute("uid"); })
      .get();

    return _.map(userids,function (uid) { return parseInt(uid,10); });
  };

  var getTo = function($button) {
    /* Get the user id of the "to" user for a submission. */
    var to_id = $button
      .closest("[transtype]")
      .find("[direction=to]")
      .find("button.active")
      .attr("uid");
    return parseInt(to_id,10);
  };

  var getAmount = function($button) {
    var amount = $button.closest("[transtype]")
      .find("input[name=amount]")
      .val();
    return parseInt(amount,10);
  };

  exports.submit = function(button) {
    $button = $(button);
    group = getGroup($button);
    debtors = getFrom($button);
    creditor = getTo($button);
    amount = getAmount($button);
    transtype = getTransType($button);
    addTrans(group,amount,debtors,creditor,transtype);
  };

})(this);

$(function () {
  $("button[role=submit]").click(function() { submit(this); });
});
