use crate::docs::module::DocumentationModule;
use crate::handle_binop;
use crate::modules::expression::expr::Expr;
use crate::modules::types::{Type, Typed};
use crate::translate::compute::{translate_computation, ArithOp};
use crate::translate::module::TranslateModule;
use crate::utils::{ParserMetadata, TranslateMetadata};
use heraclitus_compiler::prelude::*;

use super::BinOp;

#[derive(Debug, Clone)]
pub struct Sub {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

impl Typed for Sub {
    fn get_type(&self) -> Type {
        Type::Num
    }
}

impl BinOp for Sub {
    fn set_left(&mut self, left: Expr) {
        self.left = Box::new(left);
    }

    fn set_right(&mut self, right: Expr) {
        self.right = Box::new(right);
    }

    fn parse_operator(&mut self, meta: &mut ParserMetadata) -> SyntaxResult {
        token(meta, "-")?;
        Ok(())
    }
}

impl SyntaxModule<ParserMetadata> for Sub {
    syntax_name!("Sub");

    fn new() -> Self {
        Sub {
            left: Box::new(Expr::new()),
            right: Box::new(Expr::new()),
        }
    }

    fn parse(&mut self, meta: &mut ParserMetadata) -> SyntaxResult {
        let message = {
            let l_type = self.left.get_type();
            let r_type = self.right.get_type();
            format!("Cannot substract value of type '{l_type}' with value of type '{r_type}'")
        };
        let comment = "You can only substract values of type 'Num'.";
        handle_binop!(meta, self.left, self.right, message, comment, [Type::Num])?;
        Ok(())
    }
}

impl TranslateModule for Sub {
    fn translate(&self, meta: &mut TranslateMetadata) -> String {
        let left = self.left.translate(meta);
        let right = self.right.translate(meta);
        translate_computation(meta, ArithOp::Sub, Some(left), Some(right))
    }
}

impl DocumentationModule for Sub {
    fn document(&self, _meta: &ParserMetadata) -> String {
        "".to_string()
    }
}
