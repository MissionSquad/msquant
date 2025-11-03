"""Highcharts configuration helpers for GPU metrics visualization."""
from typing import Dict, Any, List
from datetime import datetime


def build_line_chart(
    title: str,
    y_label: str,
    unit: str = "",
    y_max: int = None,
    y_min: int = 0
) -> Dict[str, Any]:
    """
    Build base Highcharts configuration for a time-series line chart.
    
    Args:
        title: Chart title
        y_label: Y-axis label
        unit: Unit suffix for values
        y_max: Maximum Y value (None for auto)
        y_min: Minimum Y value
        
    Returns:
        Highcharts options dictionary
    """
    options = {
        "chart": {
            "type": "spline",
            "animation": False,
            "height": 250,
        },
        "title": {
            "text": title,
            "style": {"fontSize": "14px"}
        },
        "xAxis": {
            "type": "datetime",
            "labels": {
                "format": "{value:%H:%M:%S}"
            }
        },
        "yAxis": {
            "title": {"text": y_label},
            "min": y_min,
            "labels": {
                "format": f"{{value}}{unit}"
            }
        },
        "tooltip": {
            "valueSuffix": unit,
            "xDateFormat": "%H:%M:%S"
        },
        "legend": {
            "enabled": False
        },
        "credits": {
            "enabled": False
        },
        "series": [{
            "name": y_label,
            "data": [],
            "lineWidth": 2,
            "marker": {
                "enabled": False
            }
        }],
        "plotOptions": {
            "series": {
                "animation": False
            }
        }
    }
    
    if y_max is not None:
        options["yAxis"]["max"] = y_max
    
    return options


def convert_history_to_chart_data(
    timestamps: List[datetime],
    values: List[float]
) -> List[List[float]]:
    """
    Convert timestamp/value pairs to Highcharts data format.
    
    Args:
        timestamps: List of datetime objects
        values: List of numeric values
        
    Returns:
        List of [timestamp_ms, value] pairs
    """
    return [
        [int(ts.timestamp() * 1000), val]
        for ts, val in zip(timestamps, values)
    ]
