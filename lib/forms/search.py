#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Search form to easily find cards
"""

from flask_wtf import Form
from wtforms import StringField


class SearchForm(Form):
    """
    This is a form to search through the card collection
    """
    card_name = StringField("Name")
    card_type = StringField("Type")
    #edition = SelectField("Edition")

"""
			<div class="form-group" class="col-xs-5 control-label">
				<label for="search-edition" class="col-xs-5 control-label">Edition</label>
				<div class="col-xs-2">
					<input type="text" class="form-control" name="edition" placeholder="Edition">
				</div>
			</div>
		</div>

		<div id="colors" class="row">
			<label class="col-xs-5 control-label">Color(s)</label>
			<div class="col-xs-2">
				<input type="checkbox" name="red"> red
				<input type="checkbox" name="green"> green
				<input type="checkbox" name="white"> white
				<input type="checkbox" name="blue"> blue
				<input type="checkbox" name="black"> black
			</div>
		</div>

		<div id="rarity" class="row">
			<div class="col-xs-5"></div>
			<div class="col-xs-2">
				<div class="category">
					<div class="category-title">Rarity</div>
					<div class="category-content">
						<input type="checkbox" name="basic-land"> Basic Land
						<input type="checkbox" name="common"> Common
						<input type="checkbox" name="uncommon"> Uncommon
						<input type="checkbox" name="rare"> Rare
						<input type="checkbox" name="mythic-rare"> Mythic Rare
						<input type="checkbox" name="special"> Special
					</div>
				</div>
			</div>
		</div>
	</form>
"""
