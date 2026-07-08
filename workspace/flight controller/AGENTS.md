<INSTRUCTIONS>
{
    "codex_agent_system": {
        "version": "2.1.0",
        "environment": "Production_UAV_Routing",
        "timestamp_utc": "2026-06-24T13:17:00Z"
    },
    "agents": [
        {
            "agent_id": "route_planner_agent",
            "role": "Навігаційний ШІ-архітектор БПЛА",
            "goal": "Аналізувати зшиті масиви растрових висот і будувати оптимальний 3D-маршрут A* з мінімальними витратами енергії та обходом перешкод.",
            "backstory": "Експерт у галузі геоінформаційних систем (ГІС) та тривимірної авіаційної навігації. Здатний обробляти піксельні матриці рельєфу та перетворювати їх на безпечні ешелони польоту.",
            "llm_config": {
                "model": "gpt-4o",
                "temperature": 0.2,
                "max_tokens": 1500
            },
            "allowed_tools": [
                "raster_processor.load_and_stitch_rasters",
                "router.calculate_route"
            ],
            "constraints": {
                "min_safe_altitude_m": 120.0,
                "max_climb_angle_deg": 15.0,
                "forbidden_zones_grid_chips": []
            }
        },
        {
            "agent_id": "mission_validator_agent",
            "role": "Інспектор безпеки польотів",
            "goal": "Перевіряти згенерований агентом 'route_planner_agent' масив точок на сувору відповідність фізичним обмеженням літака та висотам рельєфу.",
            "backstory": "Автоматизований аудитор систем керування рухом. Блокує будь-які маршрути, де абсолютна висота польоту (altitude_amsl) опускається нижче безпечного буфера над точкою рельєфу (terrain_elevation).",
            "llm_config": {
                "model": "gpt-4-turbo",
                "temperature": 0.0
            },
            "allowed_tools": [
                "agent_exporter.validate_json_schema"
            ],
            "dependencies": [
                "route_planner_agent"
            ]
        }
    ],
    "agent_execution_pipeline": {
        "input_data": {
            "source_rasters": ["raster_1.png", "raster_2.png"],
            "grid_layout":,
            "start_coordinates":,
            "end_coordinates": [85, 180]
        },
        "output_format": {
            "target_file": "agent_task.json",
            "schema": "Mavlink_Compliant_V2"
        }
    }
}
</INSTRUCTIONS>
