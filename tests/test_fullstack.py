"""Verificación del flujo real entre vistas sin credenciales cloud."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from modules import oci_client

ROOT = Path(__file__).resolve().parents[1]

class FullstackFlowTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=15)
        app.session_state['authenticated'] = True
        app.session_state['username'] = 'admin'
        app.run()
        self.assertEqual(len(app.exception), 0)
        return app

    def navigate(self, app, index):
        nav = app.sidebar.radio[0]
        nav.set_value(nav.options[index]).run()
        self.assertEqual(len(app.exception), 0)

    def click(self, app, label):
        next(b for b in app.button if b.label == label).click().run()
        self.assertEqual(len(app.exception), 0)

    def test_draft_navigation_storage_and_new_batch(self):
        app = self.app()
        self.click(app, 'Ejecutar Pipeline de IA y Router Condicional')
        original = json.loads(json.dumps(app.session_state['generated_package']))
        self.navigate(app, 2)
        app.text_area(key='textarea_copy_lk').set_value('Texto revisado por el usuario').run()
        app.text_area(key='nl_res_input').set_value('Resumen editado').run()
        self.navigate(app, 3)
        self.navigate(app, 2)
        self.assertEqual(app.text_area(key='textarea_copy_lk').value, 'Texto revisado por el usuario')
        self.assertEqual(app.session_state['generated_package'], original)
        with tempfile.TemporaryDirectory() as folder, patch.object(oci_client, 'LOCAL_OCI_STORAGE_DIR', Path(folder)), patch.object(oci_client, '_obtener_cliente_oci_real', return_value=(None, None)):
            self.click(app, 'Aprobar y Guardar')
            result = app.session_state['oci_save_result']
            saved = json.loads(Path(result['ruta_local_espejo']).read_text())
            assets = saved['activos_distribucion_generados']
            self.assertEqual(assets['post_linkedin']['copy'], 'Texto revisado por el usuario')
            self.assertEqual(assets['destaque_newsletter_semanal']['resumen'], 'Resumen editado')
            self.assertTrue(app.success)
        self.navigate(app, 0)
        self.click(app, 'Caso 2: Cátedra Cloud')
        self.assertNotIn('generated_package', app.session_state)
        self.click(app, 'Ejecutar Pipeline de IA y Router Condicional')
        self.navigate(app, 2)
        self.assertNotEqual(app.text_area(key='textarea_copy_lk').value, 'Texto revisado por el usuario')

    def test_storage_failure_does_not_report_success(self):
        app = self.app()
        self.click(app, 'Ejecutar Pipeline de IA y Router Condicional')
        self.navigate(app, 2)
        with patch.object(oci_client, 'guardar_en_oci', side_effect=OSError('Sin conexión')):
            self.click(app, 'Aprobar y Guardar')
        self.assertTrue(app.error)
        self.assertNotIn('oci_save_result', app.session_state)
        self.assertFalse(app.success)

if __name__ == '__main__':
    unittest.main()
