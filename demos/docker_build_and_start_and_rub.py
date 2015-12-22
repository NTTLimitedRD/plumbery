from plumbery.engine import PlumberyEngine

engine = PlumberyEngine('fittings.yaml')
engine.build_blueprint('docker')
engine.start_nodes('docker')
engine.polish_blueprint('docker', 'rub')





