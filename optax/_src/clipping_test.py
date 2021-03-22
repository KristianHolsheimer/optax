# Lint as: python3
# Copyright 2019 DeepMind Technologies Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for optax._src.clipping."""

from absl.testing import absltest

import chex
import jax
import jax.numpy as jnp

from optax._src import clipping

STEPS = 50


class ClippingTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.init_params = (jnp.array([1., 2.]), jnp.array([3., 4.]))
    self.per_step_updates = (jnp.array([500., 5.]), jnp.array([300., 3.]))

  def test_clip(self):
    updates = self.per_step_updates
    # For a sufficiently high delta the update should not be changed.
    clipper = clipping.clip(1e6)
    clipped_updates, _ = clipper.update(updates, None)
    chex.assert_tree_all_close(clipped_updates, clipped_updates)
    # Clipping at delta=1 should make all updates exactly 1.
    clipper = clipping.clip(1.)
    clipped_updates, _ = clipper.update(updates, None)
    chex.assert_tree_all_close(
        clipped_updates, jax.tree_map(jnp.ones_like, updates))

  def test_clip_by_global_norm(self):
    updates = self.per_step_updates
    for i in range(1, STEPS + 1):
      clipper = clipping.clip_by_global_norm(1. / i)
      updates, _ = clipper.update(updates, None)
      # Check that the clipper actually works and global norm is <= max_norm
      self.assertAlmostEqual(clipping.global_norm(updates), 1. / i, places=6)
      updates_step, _ = clipper.update(self.per_step_updates, None)
      # Check that continuously clipping won't cause numerical issues.
      chex.assert_tree_all_close(updates, updates_step, atol=1e-7, rtol=1e-7)


if __name__ == '__main__':
  absltest.main()
