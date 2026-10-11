import json
import os
import unittest
from unittest.mock import patch, Mock

import soc_assistant
from analysis_contract import parse_analysis, render_analysis


def valid(event_id="idx:1"):
    return {"event_id":event_id,"disposition":"INSUFFICIENT_EVIDENCE",
            "severity":"LOW","confidence":0.4,"observed_facts":["SSH failure"],
            "hypotheses":[],"recommended_readonly_steps":["Check logs"],
            "requires_human_review":True}


class ContractTests(unittest.TestCase):
    def test_valid_json(self):
        obj=parse_analysis(json.dumps(valid()),"idx:1")
        self.assertIn("human review",render_analysis(obj,"qwen").lower())

    def test_event_id_mismatch(self):
        with self.assertRaisesRegex(ValueError,"ID mismatch"):
            parse_analysis(json.dumps(valid()),"other")

    def test_incomplete_json_and_invalid_confidence(self):
        with self.assertRaises(ValueError):
            parse_analysis('{"event_id":', "idx:1")
        o=valid()
        o["confidence"]=True
        with self.assertRaises(ValueError):
            parse_analysis(json.dumps(o),"idx:1")

    def test_no_silent_model_fallback(self):
        with patch.dict(os.environ,{"SOC_MODEL_ID":"exact-qwen"}):
            response=Mock()
            response.json.return_value={"data":[{"id":"other-model"}]}
            with patch.object(soc_assistant.requests,"get",return_value=response):
                with self.assertRaisesRegex(RuntimeError,"not available"):
                    soc_assistant.get_model()

    def test_missing_model_setting(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(RuntimeError,"SOC_MODEL_ID"):
                soc_assistant.get_model()

    def test_truncated_completion_is_rejected(self):
        response=Mock()
        response.json.return_value={"choices":[{"finish_reason":"length",
            "message":{"content":json.dumps(valid())}}]}
        with patch.object(soc_assistant.requests,"post",return_value=response):
            with self.assertRaisesRegex(ValueError,"incomplete"):
                soc_assistant.analyze("qwen","idx:1",{"full_log":"demo"})

    def test_lm_studio_uses_json_schema_not_json_object(self):
        response=Mock()
        response.json.return_value={"choices":[{"finish_reason":"stop",
            "message":{"content":json.dumps(valid())}}]}
        with patch.object(soc_assistant.requests,"post",return_value=response) as post:
            soc_assistant.analyze("qwen","idx:1",{"full_log":"demo"})
            payload=post.call_args.kwargs["json"]
            self.assertEqual(payload["response_format"]["type"],"json_schema")
            schema=payload["response_format"]["json_schema"]["schema"]
            self.assertEqual(set(schema["required"]), set(valid().keys()))
            self.assertFalse(schema["additionalProperties"])

    def test_malformed_completed_response_is_rejected(self):
        response=Mock()
        response.json.return_value={"choices":[{"finish_reason":"stop",
            "message":{"content":"not json"}}]}
        with patch.object(soc_assistant.requests,"post",return_value=response):
            with self.assertRaises(ValueError):
                soc_assistant.analyze("qwen","idx:1",{"full_log":"demo"})

if __name__=="__main__":
    unittest.main()
