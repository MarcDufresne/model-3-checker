function calculate_apr() {
    const base_price = parseFloat($("#base_price").val()) || 0;
    const trade_in = parseFloat($("#trade_in").val()) || 0;
    const tax_rate = parseFloat($("#tax_rate").val()) / 100 || 0;
    const down_payment = parseFloat($("#down_payment").val()) || 0;
    const incentive = parseFloat($("#incentive").val()) || 0;
    const apr = parseFloat($("#apr").val()) / 100 || 0;
    const term = parseInt($("#term").val());

    let tax_amount = (base_price - trade_in) * tax_rate;
    let financed_amount = base_price + tax_amount - down_payment - incentive - trade_in;
    let pmt_val = pmt(apr / 12, term, -financed_amount);
    let total_payment = term * pmt_val;
    let interests = total_payment - financed_amount;
    let cto = total_payment + down_payment;

    $("#tax_amount").val(numeral(tax_amount).format("0,0.00"));
    $("#financed_amount").val(numeral(financed_amount).format("0,0.00"));
    $("#monthly_payment").val(numeral(pmt_val).format("0,0.00"));
    $("#interests").val(numeral(interests).format("0,0.00"));
    $("#total_payment").val(numeral(total_payment).format("0,0.00"));
    $("#cto").val(numeral(cto).format("0,0.00"));
}

function pmt(int_rate, periods, present_value) {
    if (int_rate === 0)
        return present_value / periods;

    let pre_val_if = Math.pow(1 + int_rate, periods);
    return - int_rate * present_value * pre_val_if / (pre_val_if - 1);
}

$("#apr_form").submit((e) => {
    e.preventDefault();
    $("#apr_res_form")[0].reset();
    calculate_apr();
});
