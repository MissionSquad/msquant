"""Basic sanity tests for MSQuant."""
import pytest


def test_imports():
    """Test that core modules can be imported."""
    from msquant.core.quantizer import QuantizationConfig, quantize
    from msquant.core.monitoring import GPUMonitor, GPUMetrics
    from msquant.services import JobService, StorageService
    
    # Basic instantiation tests
    assert QuantizationConfig is not None
    assert quantize is not None
    assert GPUMonitor is not None
    assert GPUMetrics is not None
    assert JobService is not None
    assert StorageService is not None


def test_quantization_config_validation():
    """Test QuantizationConfig validation."""
    from msquant.core.quantizer import QuantizationConfig
    
    # Valid config should not raise
    config = QuantizationConfig(
        model_id="test/model",
        quant_method="awq",
        output_format="binary",
        calib_dataset="wikitext"
    )
    config.validate()  # Should not raise
    
    # Invalid quant_method should raise
    with pytest.raises(ValueError, match="Invalid quant_method"):
        bad_config = QuantizationConfig(
            model_id="test/model",
            quant_method="invalid",
            output_format="binary",
            calib_dataset="wikitext"
        )
        bad_config.validate()


def test_job_service_initialization():
    """Test JobService can be initialized."""
    from msquant.services import JobService
    
    service = JobService(max_log_lines=100)
    assert service.get_status().value == "idle"
    assert service.get_logs() == []
    assert service.get_result() is None
    assert service.get_error() is None


def test_storage_service_initialization():
    """Test StorageService can be initialized."""
    from msquant.services import StorageService
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        service = StorageService(
            out_dir=os.path.join(tmpdir, "out"),
            hf_home=os.path.join(tmpdir, "hf"),
            hf_datasets_cache=os.path.join(tmpdir, "hf_datasets")
        )
        
        # Check directories were created
        assert service.out_dir.exists()
        assert service.hf_home.exists()
        assert service.hf_datasets_cache.exists()
        
        # Check empty output list
        outputs = service.list_outputs()
        assert outputs == []
