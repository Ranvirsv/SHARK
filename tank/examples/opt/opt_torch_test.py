import unittest
import numpy as np
import pytest
import torch
import torch_mlir
from shark_hf_opt import OPTForCausalLM
from shark.iree_utils._common import check_device_drivers, device_driver_info
from shark.shark_inference import SharkInference
from tank.model_utils import compare_tensors
from transformers import AutoTokenizer


OPT_MODEL = "facebook/opt-1.3b"
OPT_MODEL_66B = "facebook/opt-66b"


class OPTModuleTester:
    def __init__(
        self,
        benchmark=False,
    ):
        self.benchmark = benchmark

    def create_and_check_module(self, dynamic, device, model_name):
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        # config = OPTConfig()
        # opt_model = OPTModel(config)
        opt_model = OPTForCausalLM.from_pretrained(model_name)
        opt_model.eval()
        text = "Hello my name is Bert and I love"
        inputs = tokenizer(text, return_tensors="pt")
        input_ids, attention_mask = (
            inputs.data["input_ids"],
            inputs.data["attention_mask"],
        )
        module = torch_mlir.compile(
            opt_model,
            torch.cat((input_ids, attention_mask)),
            output_type=torch_mlir.OutputType.LINALG_ON_TENSORS,
            use_tracing=True,
        )

        model_mlir = module.operation.get_asm(
            large_elements_limit=None, enable_debug_info=True
        )
        with open("OPTModule.mlir", "w") as f:
            f.write(model_mlir)
        print("Saved mlir at ./OPTModule.mlir")
        func_name = "forward"
        act_out = opt_model(input_ids, return_dict=False)
        # mlir_importer = SharkImporter(
        #    model,
        #    (input,),
        #    frontend="torch",
        # )
        # minilm_mlir, func_name = mlir_importer.import_mlir(
        #    is_dynamic=dynamic, tracing_required=True
        # )

        shark_module = SharkInference(
            model_mlir,
            device=device,
            mlir_dialect="tm_tensor",
            is_benchmark=self.benchmark,
        )
        shark_module.compile()
        results = shark_module("forward", torch.stack((input_ids, attention_mask), dim=1))
        #exp_out = tokenizer.decode(act_out[0][0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
        #shark_out = tokenizer.decode(results[0][0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
        #print("PyTorch:" + exp_out)
        #print("SHARK:" + shark_out)
        np.testing.assert_allclose(act_out[0][0].detach(), results[0][0], atol=1e-02, rtol=1e-03)

        if self.benchmark:
            shark_module.shark_runner.benchmark_all_csv(
                (input_ids, attention_mask),
                "opt",
                dynamic,
                device,
                "torch",
            )


class OPTModuleTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def configure(self, pytestconfig):
        self.module_tester = OPTModuleTester(self)
        self.module_tester.save_mlir = False
        self.module_tester.save_vmfb = False
        self.module_tester.benchmark = pytestconfig.getoption("benchmark")

    def test_350m_static_cpu(self):
        dynamic = False
        device = "cpu"
        self.module_tester.create_and_check_module(dynamic, device, OPT_MODEL)

    def test_350m_dynamic_cpu(self):
        dynamic = True
        device = "cpu"
        self.module_tester.create_and_check_module(dynamic, device, OPT_MODEL)

    @pytest.mark.skipif(
        check_device_drivers("cuda"), reason=device_driver_info("cuda")
    )
    def test_350m_static_cuda(self):
        dynamic = False
        device = "cuda"
        self.module_tester.create_and_check_module(dynamic, device, OPT_MODEL)

    @pytest.mark.skipif(
        check_device_drivers("cuda"), reason=device_driver_info("cuda")
    )
    def test_350m_dynamic_cuda(self):
        dynamic = True
        device = "cuda"
        self.module_tester.create_and_check_module(dynamic, device, OPT_MODEL)

    @pytest.mark.skipif(
        check_device_drivers("vulkan"), reason=device_driver_info("vulkan")
    )
    def test_350m_static_vulkan(self):
        dynamic = False
        device = "vulkan"
        self.module_tester.create_and_check_module(dynamic, device, OPT_MODEL)

    @pytest.mark.skipif(
        check_device_drivers("vulkan"), reason=device_driver_info("vulkan")
    )
    def test_350m_dynamic_vulkan(self):
        dynamic = True
        device = "vulkan"
        self.module_tester.create_and_check_module(dynamic, device, OPT_MODEL)

    # def test_66b_static_cpu(self):
    #    dynamic = False
    #    device = "cpu"
    #    self.module_tester.create_and_check_module(
    #        dynamic, device, OPT_MODEL_66B
    #    )

    # def test_66b_dynamic_cpu(self):
    #    dynamic = True
    #    device = "cpu"
    #    self.module_tester.create_and_check_module(
    #        dynamic, device, OPT_MODEL_66B
    #    )

    # @pytest.mark.skipif(
    #    check_device_drivers("cuda"), reason=device_driver_info("cuda")
    # )
    # def test_66b_static_cuda(self):
    #    dynamic = False
    #    device = "cuda"
    #    self.module_tester.create_and_check_module(
    #        dynamic, device, OPT_MODEL_66B
    #    )

    # @pytest.mark.skipif(
    #    check_device_drivers("cuda"), reason=device_driver_info("cuda")
    # )
    # def test_66b_dynamic_cuda(self):
    #    dynamic = True
    #    device = "cuda"
    #    self.module_tester.create_and_check_module(
    #        dynamic, device, OPT_MODEL_66B
    #    )

    # @pytest.mark.skipif(
    #    check_device_drivers("vulkan"), reason=device_driver_info("vulkan")
    # )
    # def test_66b_static_vulkan(self):
    #    dynamic = False
    #    device = "vulkan"
    #    self.module_tester.create_and_check_module(
    #        dynamic, device, OPT_MODEL_66B
    #    )

    # @pytest.mark.skipif(
    #    check_device_drivers("vulkan"), reason=device_driver_info("vulkan")
    # )
    # def test_66b_dynamic_vulkan(self):
    #    dynamic = True
    #    device = "vulkan"
    #    self.module_tester.create_and_check_module(
    #        dynamic, device, OPT_MODEL_66B
    #    )


if __name__ == "__main__":
    unittest.main()
