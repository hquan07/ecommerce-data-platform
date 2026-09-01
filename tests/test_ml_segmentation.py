import pytest
pytest.importorskip("sklearn")
import pandas as pd
from src.ml.customer_segmentation import assign_segment_names

def test_assign_segment_names():
    data = {
        'customer_unique_id': ['c1', 'c2', 'c3', 'c4'],
        'cluster_id': [0, 1, 2, 3],
        'monetary': [10.0, 1000.0, 50.0, 500.0] 
    }
    df = pd.DataFrame(data)
    
    result_df = assign_segment_names(df)
    
    # 0 (10) -> Churned/Low Value
    # 2 (50) -> At Risk
    # 3 (500) -> Promising
    # 1 (1000) -> Champions/Loyal
    
    assert result_df.loc[result_df['cluster_id'] == 0, 'segment_name'].values[0] == 'Churned/Low Value'
    assert result_df.loc[result_df['cluster_id'] == 2, 'segment_name'].values[0] == 'At Risk'
    assert result_df.loc[result_df['cluster_id'] == 3, 'segment_name'].values[0] == 'Promising'
    assert result_df.loc[result_df['cluster_id'] == 1, 'segment_name'].values[0] == 'Champions/Loyal'
