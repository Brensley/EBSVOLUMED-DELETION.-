resource "aws_cloudwatch_event_rule" "UnusedEBS_trigger" {
    name = "unusedebs-lambda-trigger"
    schedule_expression = "rate(7 days)"
    #schedule_expression = "cron(0 * * * *)"
}

resource "aws_cloudwatch_event_target" "UnusedEBS_trigger" {
    rule = "${aws_cloudwatch_event_rule.UnusedEBS_trigger.name}"
    target_id = "lambda_function"
    arn = "${aws_lambda_function.lambda_function.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda_function.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.UnusedEBS_trigger.arn}"
}
