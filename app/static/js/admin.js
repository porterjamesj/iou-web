/* globals $SCRIPT_ROOT, $ */

;(function(exports) {
  exports.addTrans = function(group_id,amount,from,to_id,kind) {
    $.ajax({
      method: "POST",
      contentType: "application/json",
      url: $SCRIPT_ROOT + "/add",
      data: JSON.stringify({"group_id":group_id,
                            "from":from,
                            "to_id":to_id,
                            "amount": amount,
                            "kind":kind})
    });
  };

  exports.submitdebt = function() {
    group_id = this.getAttribute("group");
    // assuming this is called from the right context
    debtors = $("button.debt.from.active[group=" + group_id + "]")
      .map(function () { return this.getAttribute("uid"); })
      .get();
    amount = parseFloat($("input.debt").val());
    creditor = $("button.debt.to.active[group=" + group_id + "]").attr("uid");
    exports.addTrans(group_id,amount,debtors,creditor,"debt");
  };

})(this);

$(function () {

  $("#debtsubmit").click(submitdebt);

  // $("#paysubmit").click(su);
});
