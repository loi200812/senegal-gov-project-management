/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class QRCodeField extends Component {
    static template = "senegal_gov_project_management.QRCodeWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.dialog = useService("dialog");
    }

    get imageSrc() {
        return this.props.record.data[this.props.name] 
            ? `data:image/png;base64,${this.props.record.data[this.props.name]}`
            : null;
    }

    onClickEnlarge() {
        if (!this.imageSrc) return;
        
        this.dialog.add(QRCodeDialog, {
            imageSrc: this.imageSrc,
        });
    }
}

class QRCodeDialog extends Component {
    static template = "senegal_gov_project_management.QRCodeDialog";
    static props = ["close", "imageSrc"];

    downloadQRCode() {
        const link = document.createElement('a');
        link.href = this.props.imageSrc;
        link.download = 'qr_code.png';
        link.click();
    }
}

registry.category("fields").add("qr_code", QRCodeField);

});